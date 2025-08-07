from selenium import webdriver
from selenium.webdriver.safari.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import platform
import sys
import subprocess

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

def check_and_install_libraries():
    required_libraries = ["selenium"]
    # Safari는 webdriver-manager가 필요하지 않습니다.
    for lib in required_libraries:
        try:
            __import__(lib)
        except ImportError:
            print(f"{lib} 라이브러리가 설치되어 있지 않습니다. 설치를 시도합니다...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
                print(f"{lib} 라이브러리 설치 완료.")
            except subprocess.CalledProcessError as e:
                print(f"오류: {lib} 라이브러리 설치에 실패했습니다. {e}")
                print("pip가 올바르게 설치되어 있고 PATH에 추가되어 있는지 확인해주세요.")
                sys.exit(1)

def main():
    check_and_install_libraries() # 라이브러리 설치 확인 및 설치

    if platform.system() != "Darwin":
        print("이 스크립트는 macOS에서만 실행할 수 있습니다 (Safari 브라우저).")
        return

    driver = None
    try:
        # SafariDriver는 Safari 브라우저를 자동으로 시작합니다.
        # Safari -> 개발자용 -> 원격 자동화 허용을 활성화해야 합니다.
        print("Safari 브라우저 시작 중...")
        driver = webdriver.Safari()
        print("Safari 브라우저가 시작되었습니다.")

        previous_url = None
        print("URL 변경을 모니터링 중입니다. 중지하려면 Ctrl+C를 누르세요.")
        while True:
            # 페이지 로드가 완료될 때까지 기다립니다.
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            current_url = driver.current_url
            if current_url != previous_url:
                print(f"URL이 변경되었습니다: {current_url}")
                inject_script(driver, JS_CODE)
                previous_url = current_url
            time.sleep(1) # 1초마다 URL 확인

    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
        print("Safari -> 개발자용 -> 원격 자동화 허용이 활성화되어 있는지 확인해주세요.")
        print("macOS에 Safari 브라우저가 설치되어 있는지 확인해주세요.")
    finally:
        if driver:
            print("모니터링이 중지되었습니다. Safari 브라우저를 종료합니다.")
            driver.quit()

if __name__ == "__main__":
    main()