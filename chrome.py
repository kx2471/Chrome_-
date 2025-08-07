from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import subprocess
import platform
import os
import tempfile
import shutil
# import sys # sys 모듈은 더 이상 필요하지 않으므로 제거

# 주입할 JavaScript 코드
JS_CODE = """
(function () {
  const existing = document.getElementById('grid-overlay');
  if (existing) {
    existing.remove();
    window.removeEventListener('resize', updateGrid);
    return;
  }

  const overlay = document.createElement('div');
  overlay.id = 'grid-overlay';
  Object.assign(overlay.style, {
    position: 'absolute',
    top: '0',
    left: '0',
    width: '100vw',
    height: `${document.body.scrollHeight}px`,
    pointerEvents: 'none',
    zIndex: '9999',
    display: 'flex',
    boxSizing: 'border-box',
    justifyContent: 'flex-start',
  });

  function updateGrid() {
    overlay.innerHTML = '';
    overlay.style.height = `${document.body.scrollHeight}px`;
    const w = window.innerWidth;
    let columns = 12, gutter = 24, margin = 24;

    if (w >= 360 && w <= 767) {
      columns = 4; gutter = 16; margin = 16;
    } else if (w >= 768 && w <= 1023) {
      columns = 8; gutter = 16; margin = 24;
    } else if (w >= 1024 && w <= 1279) {
      columns = 12; gutter = 24; margin = 24;
    } else if (w >= 1280) {
      columns = 12; gutter = 24; margin = 24;
    }

    overlay.style.paddingLeft = `${margin}px`;
    overlay.style.paddingRight = `${margin}px`;

    const totalGutter = gutter * (columns - 1);
    const contentWidth = w - (margin * 2);
    const columnWidth = (contentWidth - totalGutter) / columns;

    for (let i = 0; i < columns; i++) {
      const col = document.createElement('div');
      Object.assign(col.style, {
        width: `${columnWidth}px`,
        height: '100%',
        backgroundColor: 'rgba(255, 182, 193, 0.2)',
        marginRight: i < columns - 1 ? `${gutter}px` : '0',
      });
      overlay.appendChild(col);
    }

    console.log(`viewport: ${w}px → columns: ${columns}, gutter: ${gutter}px, margin: ${margin}px`);
  }

  window.addEventListener('resize', updateGrid);
  updateGrid();
  document.body.appendChild(overlay);
})();
"""

def inject_script(driver, script):
    """주어진 JavaScript 코드를 현재 웹페이지에 주입합니다."""
    try:
        driver.execute_script(script)
        print("JavaScript가 성공적으로 주입되었습니다.")
    except Exception as e:
        print(f"스크립트 주입 오류: {e}")

# check_and_install_libraries 함수 제거

def find_chrome_executable():
    """운영체제에 따라 Chrome 실행 파일의 경로를 찾습니다.
    찾지 못할 경우 None을 반환합니다.
    """
    # 사용자가 직접 경로를 지정하고 싶을 때 이 변수를 사용합니다.
    # 예: CHROME_PATH_OVERRIDE = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    CHROME_PATH_OVERRIDE = None # 여기에 Chrome 실행 파일의 전체 경로를 지정할 수 있습니다.

    if CHROME_PATH_OVERRIDE and os.path.exists(CHROME_PATH_OVERRIDE):
        return CHROME_PATH_OVERRIDE

    # shutil.which를 사용하여 PATH에서 Chrome을 찾습니다.
    chrome_path = shutil.which("google-chrome") or \
                  shutil.which("chrome") or \
                  shutil.which("chromium")
    if chrome_path:
        return chrome_path

    # 일반적인 설치 경로를 확인합니다.
    if platform.system() == "Windows":
        paths = [
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe")
        ]
    elif platform.system() == "Darwin": # macOS
        paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        ]
    elif platform.system() == "Linux":
        paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/opt/google/chrome/google-chrome"
        ]
    else:
        return None

    for path in paths:
        if os.path.exists(path):
            return path

    return None

def launch_chrome_for_debugging():
    """Chrome을 원격 디버깅 모드로 실행합니다.
    운영체제에 따라 Chrome 실행 경로를 자동으로 찾습니다.
    """
    chrome_path = find_chrome_executable()

    if not chrome_path:
        print("오류: Chrome 실행 파일을 찾을 수 없습니다.")
        print("Chrome이 설치되어 있는지 확인하거나, 스크립트 내의 'CHROME_PATH_OVERRIDE' 변수에")
        print("Chrome 실행 파일의 정확한 경로를 지정해주세요.")
        return None, None

    # 실행할 때마다 고유한 임시 사용자 데이터 디렉토리 생성
    user_data_dir = tempfile.mkdtemp(prefix="chrome_dev_profile_")
    print(f"임시 사용자 데이터 디렉토리 생성: {user_data_dir}")

    command = [
        chrome_path,
        "--remote-debugging-port=9222",
        f"--user-data-dir={user_data_dir}",
        "--no-first-run", # 첫 실행 마법사 건너뛰기
        "--no-default-browser-check", # 기본 브라우저 확인 건너뛰기
        "about:blank" # Chrome이 바로 브라우저 창을 띄우도록 기본 URL 지정
    ]

    print(f"Chrome 실행 중: {' '.join(command)}")
    # subprocess.Popen을 사용하여 백그라운드에서 Chrome 실행
    # shell=True는 Windows에서 경로에 공백이 있을 때 필요할 수 있습니다.
    # macOS/Linux에서는 shell=False가 더 안전합니다.
    if platform.system() == "Windows":
        # Windows에서는 경로에 공백이 있을 수 있으므로, 실행 파일 경로만 따옴표로 묶어줍니다.
        # 나머지 인자들은 그대로 전달합니다.
        if ' ' in chrome_path and not (chrome_path.startswith('"') and chrome_path.endswith('"')):
            quoted_chrome_path = f'"{chrome_path}"'
        else:
            quoted_chrome_path = chrome_path

        # 명령어를 하나의 문자열로 구성하여 shell=True로 실행
        full_command_str = f"{quoted_chrome_path} {' '.join(command[1:])}"
        process = subprocess.Popen(full_command_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print("Chrome이 시작될 때까지 잠시 기다립니다...")
    time.sleep(5) # Chrome이 완전히 시작될 때까지 기다립니다.
    return process, user_data_dir

def main():
    # check_and_install_libraries() # 라이브러리 설치 확인 및 설치 로직 제거

    chrome_process = None
    user_data_dir = None
    driver = None
    try:
        chrome_process, user_data_dir = launch_chrome_for_debugging()
        if not chrome_process:
            print("Chrome을 시작할 수 없어 종료합니다.")
            return

        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

        print("Chrome 브라우저에 연결 시도 중...")
        driver = webdriver.Chrome(options=chrome_options)
        print("Chrome 브라우저에 성공적으로 연결되었습니다.")

        previous_url = None
        print("URL 변경을 모니터링 중입니다. 중지하려면 Ctrl+C를 누르세요.")
        while True:
            current_url = driver.current_url
            if current_url != previous_url:
                print(f"URL이 변경되었습니다: {current_url}")
                inject_script(driver, JS_CODE)
                previous_url = current_url
            time.sleep(1) # 1초마다 URL 확인

    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
        print("Chrome이 올바르게 시작되었는지, 그리고 다른 Chrome 인스턴스가 디버깅 포트를 사용하고 있지 않은지 확인해주세요.")
    finally:
        if driver:
            # 사용자가 브라우저를 제어하므로 드라이버를 종료하지 않습니다.
            print("모니터링이 중지되었습니다. 브라우저는 사용자 제어 상태로 유지됩니다.")
        if chrome_process:
            # 스크립트가 시작한 Chrome 프로세스를 종료하지 않습니다.
            # 사용자가 직접 닫도록 합니다.
            pass
        # 임시 디렉토리는 브라우저가 닫힌 후에 수동으로 정리해야 합니다.
        # if user_data_dir and os.path.exists(user_data_dir):
        #     shutil.rmtree(user_data_dir)

if __name__ == "__main__":
    main()