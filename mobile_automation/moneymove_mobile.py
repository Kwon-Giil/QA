import os
import time
import re
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException

# .env 파일 로드
load_dotenv()

def run_moneymove_test():
    # Appium 구동 환경 정의
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
        
        # 🔐 .env 파일에서 PIN 값을 가져와서 6자리 리스트로 변환
        pin_str = os.getenv('PIN', '123456')
        pin_code = list(pin_str)

        # 핀 번호 입력 
        print(f"🔐 핀 번호 입력 시작 (총 {len(pin_code)}자리)...")
        for digit in pin_code:
            digit_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, f'//*[@text="{digit}"]'))
            )
            digit_button.click()
            time.sleep(0.3)  # 터치 간격 유지
            
        print("✨ 핀 번호 입력이 완료되었습니다!")
        time.sleep(3)  # 로그인 후 메인 화면 진입 대기

        sold_out_xpath = '//android.view.View[@resource-id="wrap"]/android.view.View[2]/android.view.View[2]/android.view.View/android.view.View/android.view.View[2]//android.widget.TextView[@text="투자가 모두 마감되었습니다."]'

        try:
            # 짧은 대기 시간(2초) 동안 마감 문구가 화면에 나타나는지 확인
            sold_out_element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((AppiumBy.XPATH, sold_out_xpath))
            )
            print("==========================================")
            print("[테스트 종료] 투자가 모두 마감되었습니다. 진행 가능한 상품이 없습니다.")
            print("사유: 마감된 상품으로 인한 투자 프로세스 조기 종료 (Graceful Exit)")
            print("==========================================")
            return False  # 에러가 아닌 비즈니스 로직상 정상 종료
        
        except Exception:
            print("투자 가능 상품 확인: 투자 테스트 시작")

        print("🔍 content-desc 속성을 이용해 가장 위에 있는 첫 번째 상품의 '상세보기' 버튼 찾는 중...")

        # 1. content-desc 속성과 인덱스 [1]을 조합한 범용 XPath 적용
        first_detail_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '(//android.widget.Button[@content-desc="상세보기 바로가기"])[1]')
            )
        )

        # 2. 버튼 클릭 실행
        first_detail_button.click()
        time.sleep(3)
        print("✨ 첫 번째 상품 상세 페이지 진입 성공!")

        # 1. 'TK_'로 시작하는 채권 번호 탐색 및 스크롤
        scroll_to_bond = (
            'new UiScrollable(new UiSelector().scrollable(true))'
            '.scrollIntoView(new UiSelector().textStartsWith("TK_"))'
        )

        try:
            bond_element = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, scroll_to_bond)
            bond_number = bond_element.text
            print(f"[성공] 가져온 채권 번호: {bond_number}")
        except NoSuchElementException:
            print("[오류] 채권 번호 미출력")

        # 2. '상품 선택하기' 버튼까지 스크롤 후 클릭
        scroll_to_button = (
            'new UiScrollable(new UiSelector().scrollable(true))'
            '.scrollIntoView(new UiSelector().text("상품 선택하기"))'
        )

        select_btn = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, scroll_to_button)
        select_btn.click()
        print("[성공] '상품 선택하기' 버튼 클릭 완료")
        time.sleep(3)  # 버튼 클릭 후 대기

        # 상품 선택 후 하단 버튼이 정상적으로 활성화되는지 검증 부분
        try:
            active_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, '//android.widget.Button[contains(@text, "개 상품 투자금액 설정하기")]'))
            )

            btn_text = active_btn.text
            print(f"[성공] 버튼 상태 전이 확인 완료: '{btn_text}' (버튼 활성화 정상)")

            # 활성화된 버튼 클릭
            active_btn.click()
            time.sleep(2)

        except Exception as btn_err:
            print("==========================================")
            print("[테스트 실패 / 버그 발견] 상품 선택 후 버튼이 활성화되지 않았습니다.")
            print("==========================================")
            raise AssertionError(f"버그 검출: 상품을 선택했음에도 투자 진행 버튼이 활성화되지 않았습니다. 원인: {btn_err}")

        # --------------------------------------------------------------------
        # 예치금 잔액 확인 및 조건부 재시도 로직 (AlertDialog 경로 및 팝업 핸들링 포함)
        # --------------------------------------------------------------------
        balance = 0  # NameError 방지용 안전 초기화
        
        balance_xpath = '//android.app.AlertDialog/android.view.View[3]/android.widget.ListView[1]/android.view.View[4]//android.view.View[contains(@text, "원")]'

        try:
            balance_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((AppiumBy.XPATH, balance_xpath))
            )
            balance_text = balance_element.text  # 예: "10,984 원"
            
            print(f"[디버그] 앱에서 읽어온 정확한 잔액 텍스트: '{balance_text}'")
            
            numbers_only = re.sub(r'[^0-9]', '', balance_text)
            balance = int(numbers_only) if numbers_only else 0
            
            print(f"[정보] 최초 확인된 예치금 잔액: {balance:,}원")
            
        except Exception as e:
            print(f"[경고] 지정된 AlertDialog 경로에서 예치금 잔액을 읽지 못했습니다. 원인: {e}")
            balance = 0

        # 잔액이 1만원 미만인 경우에만 '입금확인' 재시도 루프(for문) 진입
        if balance < 10000:
            print("[안내] 잔액이 1만원 미만입니다. 입금 확인 재시도를 시작합니다.")
            max_retries = 3
            
            for attempt in range(1, max_retries + 1):
                try:
                    # 1. '입금확인' 버튼 클릭
                    deposit_check_btn = driver.find_element(AppiumBy.XPATH, '//android.widget.Button[@text="입금확인"]')
                    deposit_check_btn.click()
                    time.sleep(1)  # 팝업 렌더링 대기
                    
                    # 2. 입금확인 후 뜨는 안내 팝업의 '확인' 버튼 클릭 처리 (AlertDialog 팝업 닫기)
                    popup_confirm_xpath = '//androidx.compose.ui.viewinterop.ViewFactoryHolder/android.webkit.WebView/android.webkit.WebView/android.view.View/android.app.AlertDialog//android.widget.Button[@text="확인"]'
                    popup_confirm_btn = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((AppiumBy.XPATH, popup_confirm_xpath))
                    )
                    popup_confirm_btn.click()
                    print(f"[안내] 입금 확인 팝업 '확인' 버튼 클릭 완료 (시도 {attempt}/{max_retries})")
                    
                    time.sleep(2)  # 서버 입금 반영 대기 딜레이
                    
                except Exception as popup_err:
                    print(f"[알림] 입금확인 버튼 클릭 또는 팝업 처리 중 예외 발생 (시도 {attempt}/{max_retries}): {popup_err}")

                # 3. 팝업이 닫힌 후 잔액 재조회
                try:
                    balance_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((AppiumBy.XPATH, balance_xpath))
                    )
                    balance_text = balance_element.text
                    print(f"[디버그] 재시도 {attempt} - 읽어온 원본 잔액 텍스트: '{balance_text}'")
                    
                    numbers_only = re.sub(r'[^0-9]', '', balance_text)
                    balance = int(numbers_only) if numbers_only else 0
                    
                    print(f"[정보] 재시도 {attempt}/{max_retries} - 현재 잔액: {balance:,}원")
                except Exception as sub_err:
                    print(f"[알림] 재시도 중 잔액 재조회 실패: {sub_err}")

                # 4. 재시도 도중 1만원 이상으로 채워졌다면 즉시 루프 탈출
                if balance >= 10000:
                    print("[성공] 입금 반영 완료! 1만원 이상이 확인되었습니다.")
                    break

        # 잔액 부족 시 테스트 종료 처리
        if balance < 10000:
            print("==========================================")
            print("[테스트 종료] 입금 반영을 시도했으나 예치금이 여전히 1만원 미만입니다.")
            print("사유: 잔액 부족으로 인한 투자 진행 불가 (정상 종료)")
            print("==========================================")
            return False  # 비즈니스 로직상 정상 종료
        else:
            print("[성공] 예치금 1만원 이상 검증 통과! 다음 투자 진행 단계로 넘어갑니다.")
            # TODO: 금액 입력 및 최종 투자하기 버튼 클릭 후속 로직 연결
            return True

    except Exception as e:
        print(f"❌ 자동화 테스트 진행 중 오류 발생: {e}")
        raise

    finally:
        print("🧹 테스트 완료: 머니무브 앱을 강제 종료하고 세션을 닫습니다.")
        try:
            driver.terminate_app('ai.moneymove.intergrate')
        except Exception as term_err:
            print(f"⚠️ 앱 종료 중 예외 발생: {term_err}")
            
        driver.quit()

if __name__ == '__main__':
    run_moneymove_test()