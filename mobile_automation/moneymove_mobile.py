import os
import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def run_moneymove_test():
    options = UiAutomator2Options()
    options.platform_name = 'Android'
    options.automation_name = 'UiAutomator2'
    options.device_name = 'R3CN30P6K6Z'
    
    # 대상 앱 패키지 및 스플래시 액티비티 설정
    options.app_package = 'ai.moneymove.intergrate'
    options.app_activity = 'ai.moneymove.feature.splash.SplashActivity'
    
    options.no_reset = True
    options.set_capability('appium:forceAppLaunch', True)

    appium_server_url = 'http://localhost:4723'

    print("🚀 앱피움 서버 연결 및 머니무브 앱 강제 실행 중...")
    driver = webdriver.Remote(appium_server_url, options=options)

    try:
        print("✅ 앱이 성공적으로 실행되었습니다!")
        
        # 명시적 대기 설정 (최대 10초)
        wait = WebDriverWait(driver, 10)
        
        # 🔐 .env 파일에서 PIN 값을 가져와서 6자리 리스트로 변환 (기본값 설정 가능)
        pin_str = os.getenv('PIN', '123456')
        pin_code = list(pin_str)
        
        print(f"🔐 핀 번호 입력 시작 (총 {len(pin_code)}자리)...")
        for digit in pin_code:
            # TextView/Button 형제 구조와 상관없이 text 속성만 정확히 타겟팅하는 범용 XPath
            digit_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, f'//*[@text="{digit}"]'))
            )
            digit_button.click()
            time.sleep(0.5)  # 터치 간격 유지
            
        print("✨ 핀 번호 입력이 완료되었습니다!")
        time.sleep(3)  # 로그인 후 메인 화면 진입 대기

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

    finally:
        print("🧹 테스트 완료: 머니무브 앱을 강제 종료하고 세션을 닫습니다.")
        try:
            driver.terminate_app('ai.moneymove.intergrate')
        except Exception as term_err:
            print(f"⚠️ 앱 종료 중 예외 발생: {term_err}")
            
        driver.quit()

if __name__ == '__main__':
    run_moneymove_test()