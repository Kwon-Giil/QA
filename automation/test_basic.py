from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import time
import os

# .env 파일에서 환경 변수 불러오기
load_dotenv()

# 환경 변수에서 안전하게 아이디/비밀번호 가져오기
USER_ID = os.getenv("MONEYMOVE_ID")
USER_PW = os.getenv("MONEYMOVE_PW")

def test_moneymove_login():

    with sync_playwright() as p:
        # 1. 브라우저 실행 (화면이 보이도록 headless=False 설정)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 2. moneymove.ai 접속
        print("moneymove.ai 접속 중...")
        page.goto("https://moneymove.ai/")

        # 3. 페이지 타이틀 확인
        print(f"페이지 타이틀: {page.title()}")
        time.sleep(2) # 페이지 로딩 대기

        # 4. '로그인' 텍스트를 가진 요소 찾아 클릭
        print("로그인 버튼 찾는 중...")
           
        page.get_by_text("로그인").first.click()
        time.sleep(2) # 로그인 페이지 로딩 대기

        # 로그인 페이지 로딩 대기 및 아이디/비밀번호 입력
        print("아이디 및 비밀번호 입력 중...")
        
        # 아이디 입력창 찾아서 채우기 
        # (type이 email이거나 텍스트 계열인 input을 타겟팅)
        page.locator("#userId").fill(USER_ID)
        
        # 비밀번호 입력창 찾아서 채우기
        page.locator("#loginPassword").fill(USER_PW)

        print("로그인 정보 입력 완료!")
        
        # 최종 로그인 제출 버튼 클릭 (필요시 활성화)
        page.get_by_role("button", name="로그인").last.click()
        
        # 5. 결과 확인을 위해 3초 대기
        page.wait_for_timeout(3000)

        # 6. 브라우저 종료
        browser.close()
        print("테스트 완료!")

if __name__ == "__main__":
    test_moneymove_login()