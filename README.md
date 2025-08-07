# UI 스크립트 주입 도구

이 프로젝트는 Python과 Selenium을 사용하여 Chrome 브라우저에 JavaScript 코드를 자동으로 주입하는 도구입니다. 사용자가 Chrome 브라우저에서 URL을 변경할 때마다 지정된 JavaScript 코드가 웹 페이지에 삽입됩니다.

## 주요 기능

*   **자동 Chrome 실행:** 스크립트 실행 시 Chrome 브라우저를 원격 디버깅 모드로 자동으로 시작합니다.
*   **새로운 프로필 사용:** 매번 새로운 임시 사용자 프로필로 Chrome을 시작하여 로그인 정보나 캐시 없이 깨끗한 상태를 유지합니다.
*   **URL 변경 감지:** Chrome 브라우저의 URL 변경을 실시간으로 감지합니다.
*   **JavaScript 주입:** URL이 변경될 때마다 미리 정의된 JavaScript 코드를 현재 웹 페이지에 주입합니다. (예: UI 그리드 오버레이)
*   **운영체제 호환성:** Windows 및 macOS 환경을 지원합니다.

## 사용 방법

1.  **필수 라이브러리 설치:**
    ```bash
    pip install selenium webdriver-manager
    ```

2.  **브라우저별 스크립트 실행:**

    ### Chrome (`chrome.py`)

    *   **특징:** 기존 Chrome 인스턴스에 연결하여 사용자가 제어하는 브라우저에 스크립트를 주입합니다. 스크립트 실행 시 새로운 임시 프로필로 Chrome이 자동으로 시작됩니다.
    *   **실행:**
        ```bash
        python chrome.py
        ```

    ### Edge (`edge.py`)

    *   **특징:** Chrome과 유사하게 기존 Edge 인스턴스에 연결하여 사용자가 제어하는 브라우저에 스크립트를 주입합니다. 스크립트 실행 시 새로운 임시 프로필로 Edge가 자동으로 시작됩니다.
    *   **실행:**
        ```bash
        python edge.py
        ```

    ### Safari (`safari.py`)

    *   **특징:** macOS에서만 실행 가능합니다. Selenium은 Safari의 기존 인스턴스에 연결하는 것을 지원하지 않으므로, 스크립트 실행 시 **새로운 Safari 브라우저 인스턴스를 시작**합니다.
    *   **사전 설정 (필수):**
        1.  Safari를 엽니다.
        2.  메뉴 바에서 `Safari` > `설정` (또는 `환경설정`)을 클릭합니다.
        3.  `고급` 탭으로 이동합니다.
        4.  "메뉴 막대에서 개발자용 메뉴 보기"를 체크합니다.
        5.  메뉴 바에 새로 생긴 `개발자용` 메뉴를 클릭하고 `원격 자동화 허용`을 체크합니다.
    *   **실행:**
        ```bash
        python safari.py
        ```

3.  **스크립트 중지:**
    터미널에서 `Ctrl+C`를 눌러 스크립트를 중지할 수 있습니다. 스크립트가 종료되어도 Chrome 및 Edge 브라우저는 계속 열려 있으며, Safari는 자동으로 종료됩니다.

## 브라우저 실행 파일 경로 문제 해결

만약 스크립트가 브라우저 실행 파일을 자동으로 찾지 못한다면, 해당 스크립트 파일 상단에 있는 `CHROME_PATH_OVERRIDE`, `EDGE_PATH_OVERRIDE` 변수에 브라우저 실행 파일의 정확한 전체 경로를 직접 지정할 수 있습니다.

**예시 (`chrome.py` 파일 내에서):**

```python
# chrome.py 파일 내에서
CHROME_PATH_OVERRIDE = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" # Windows 예시
# 또는
# CHROME_PATH_OVERRIDE = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" # macOS 예시
```