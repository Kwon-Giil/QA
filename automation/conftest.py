import pytest
from playwright.sync_api import sync_playwright
import os

@pytest.fixture(scope="function")
def page():
    """환경(로컬 vs CI)에 따라 Headless 모드를 자동으로 전환하는 Fixture"""
    
    # GitHub Actions 등 CI 환경이거나 환경변수가 설정된 경우 Headless=True
    is_ci = os.getenv("CI", "false").lower() == "true"
    headless_mode = os.getenv("HEADLESS", str(is_ci)).lower() == "true"

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless_mode, 
            # 헤드리스 모드일 때는 최대화 창 인자가 의미 없으므로 로컬(False)일 때만 적용
            args=["--start-maximized"] if not headless_mode else []
        )
        
        # 헤드리스 환경에서는 뷰포트 크기를 명시해주어야 UI 깨짐을 방지할 수 있습니다.
        context_args = {"no_viewport": True} if not headless_mode else {"viewport": {"width": 1920, "height": 1080}}
        
        context = browser.new_context(**context_args)
        page = context.new_page()
        
        yield page
        browser.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """테스트 실패 시 자동으로 스크린샷을 찍어주는 훅(Hook)"""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page", None)
        if page:
            os.makedirs("screenshots", exist_ok=True)
            screenshot_path = f"screenshots/{item.name}_fail.png"
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"\n❌ [TEST FAILED] 스크린샷 저장됨: {screenshot_path}")