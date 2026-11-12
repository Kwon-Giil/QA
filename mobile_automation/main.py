import os
from dotenv import load_dotenv
from appium import webdriver
from appium.options.android import UiAutomator2Options

from pages.login_page import LoginPage
from pages.invest_page import InvestPage
from pages.cancel_page import CancelPage

load_dotenv()

def run_moneymove_test():
    options = UiAutomator2Options()
    options.platform_name = 'Android'
    options.automation_name = 'UiAutomator2'
    options.device_name = 'R3CN30P6K6Z'
    options.app_package = 'ai.moneymove.intergrate'
    options.app_activity = 'ai.moneymove.feature.splash.SplashActivity'
    options.no_reset = True
    options.set_capability('appium:forceAppLaunch', True)

    driver = webdriver.Remote('http://localhost:4723', options=options)

    try:
        print("🚀 앱피움 서버 연결 및 머니무브 앱 강제 실행 중...")
        
        # 페이지 객체 인스턴스 생성
        login_page = LoginPage(driver)
        invest_page = InvestPage(driver)
        cancel_page = CancelPage(driver)

        # 1. 로그인
        login_page.login_with_pin()

        # 2. 마감 체크 및 상품 선택
        if invest_page.check_sold_out():
            return False
        
        invest_page.select_first_product()
        bond_text = invest_page.get_bond_text()
        invest_page.proceed_to_amount_setting()

        # 3. 잔액 확인 및 금액 입력
        initial_balance, current_balance = invest_page.verify_and_handle_balance()
        invest_page.enter_investment_amount(current_balance)
        invest_page.submit_final_investment()

        # 4. 약관 동의 및 리뷰 처리
        invest_page.handle_agreements_and_review()

        # 5. 취소 및 잔액 검증
        cancel_page.cancel_investment(bond_text, initial_balance)

        return True

    except Exception as e:
        print(f"❌ 자동화 테스트 진행 중 오류 발생: {e}")
        raise

    finally:
        print("🧹 테스트 완료: 머니무브 앱을 종료합니다.")
        try:
            driver.terminate_app('ai.moneymove.intergrate')
        except Exception:
            pass
        driver.quit()

if __name__ == '__main__':
    run_moneymove_test()