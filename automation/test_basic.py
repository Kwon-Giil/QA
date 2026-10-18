from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from dotenv import load_dotenv
import os

# 1. 환경 변수 로드
load_dotenv()
USER_ID = os.getenv("MONEYMOVE_ID")
USER_PW = os.getenv("MONEYMOVE_PW")

def test_moneymove_login():
    with sync_playwright() as p:
        # 브라우저 실행
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("🚀 moneymove.ai 접속 중...")
        page.goto("https://moneymove.ai/")
        
        # 2. 메인 페이지의 '로그인' 버튼 클릭 (텍스트로 안정적으로 타겟팅)
        print("로그인 페이지로 이동 중...")
        page.get_by_text("로그인").first.click()
        
        # 3. 아이디 및 비밀번호 입력
        print("아이디/비밀번호 입력 중...")
        page.locator("#userId").fill(USER_ID)
        page.locator("#loginPassword").fill(USER_PW)
        
        # 4. 로그인 버튼 클릭 
        # (만약 아래 셀렉터로 안 눌리면 실제 제출 버튼의 텍스트나 클래스로 수정 필요)
        print("로그인 버튼 클릭!")
        page.locator("button[onclick*='loginConfirm']").click()
        
        try:            
            # 결과 검증 (실패 팝업 vs 성공 마이페이지 버튼)
            error_popup = page.locator("#alertPopup")
            my_page_btn = page.locator("a.btn-gnb[href*='/invest/my-page/main']")
            
            # 실패 팝업이 뜨는 경우 (타임아웃 4초)
            if error_popup.is_visible(timeout=4000):
                fail_title = page.locator("#alert-title").inner_text()
                fail_contents = page.locator("#alert-contents").inner_text()
                print(f"로그인 실패: [{fail_title}] {fail_contents}")
            
            # 마이페이지 버튼이 보이는 경우 (타임아웃 6초)
            elif my_page_btn.is_visible(timeout=6000):
                print("로그인 성공!")
            
            # 둘 다 해당 안 될 때
            else:
                print("[WARNING] 상태 불명")

        except Exception as e:
            # 🚨 예기치 않은 에러 발생 시 스크린샷 저장
            print(f"[CRITICAL ERROR] 예외 발생: {e}")
            page.screenshot(path="login_error_debug.png", full_page=True)
            print("디버깅용 스크린샷 저장 완료: login_error_debug.png")
        
        # 테스트 확인을 위해 잠시 대기 (필요시 제거 가능)
    input("테스트 완료")
    browser.close()

if __name__ == "__main__":
    test_moneymove_login()