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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions import interaction

# .env 파일 로드
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

    appium_server_url = 'http://localhost:4723'

    print("🚀 앱피움 서버 연결 및 머니무브 앱 강제 실행 중...")
    driver = webdriver.Remote(appium_server_url, options=options)

    try:
        print("✅ 앱이 성공적으로 실행되었습니다!")
        wait = WebDriverWait(driver, 10)
        
        # 🔐 핀 번호 입력
        pin_str = os.getenv('PIN', '123456')
        pin_code = list(pin_str)

        print(f"🔐 핀 번호 입력 시작 (총 {len(pin_code)}자리)...")
        for digit in pin_code:
            digit_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, f'//*[@text="{digit}"]'))
            )
            digit_button.click()
            time.sleep(0.3)
            
        print("✨ 핀 번호 입력이 완료되었습니다!")
        time.sleep(3)

        sold_out_xpath = '//android.view.View[@resource-id="wrap"]/android.view.View[2]/android.view.View[2]/android.view.View/android.view.View/android.view.View[2]//android.widget.TextView[@text="투자가 모두 마감되었습니다."]'

        try:
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((AppiumBy.XPATH, sold_out_xpath))
            )
            print("==========================================")
            print("[테스트 종료] 투자가 모두 마감되었습니다. 진행 가능한 상품이 없습니다.")
            print("==========================================")
            return False
        except Exception:
            print("투자 가능 상품 확인: 투자 테스트 시작")

        print("🔍 첫 번째 상품의 '상세보기' 버튼 찾는 중...")
        first_detail_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '(//android.widget.Button[@content-desc="상세보기 바로가기"])[1]')
            )
        )
        first_detail_button.click()
        time.sleep(3)

        scroll_to_bond = (
            'new UiScrollable(new UiSelector().scrollable(true))'
            '.scrollIntoView(new UiSelector().textStartsWith("TK_"))'
        )
        try:
            bond_element = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, scroll_to_bond)
            print(f"[성공] 가져온 채권 번호: {bond_element.text}")
        except NoSuchElementException:
            print("[오류] 채권 번호 미출력")

        scroll_to_button = (
            'new UiScrollable(new UiSelector().scrollable(true))'
            '.scrollIntoView(new UiSelector().text("상품 선택하기"))'
        )
        select_btn = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, scroll_to_button)
        select_btn.click()
        time.sleep(3)

        try:
            active_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, '//android.widget.Button[contains(@text, "개 상품 투자금액 설정하기")]'))
            )
            active_btn.click()
            time.sleep(2)
        except Exception as btn_err:
            raise AssertionError(f"버그 검출: 상품을 선택했음에도 투자 진행 버튼이 활성화되지 않았습니다. 원인: {btn_err}")

        balance = 0  
        balance_xpath = '//android.app.AlertDialog/android.view.View[3]/android.widget.ListView[1]/android.view.View[4]//android.view.View[contains(@text, "원")]'

        try:
            balance_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((AppiumBy.XPATH, balance_xpath))
            )
            numbers_only = re.sub(r'[^0-9]', '', balance_element.text)
            balance = int(numbers_only) if numbers_only else 0
            print(f"[정보] 최초 확인된 예치금 잔액: {balance:,}원")
        except Exception as e:
            balance = 0

        if balance < 10000:
            print("[안내] 잔액이 1만원 미만입니다. 입금 확인 재시도를 시작합니다.")
            for attempt in range(1, 4):
                try:
                    deposit_check_btn = driver.find_element(AppiumBy.XPATH, '//android.widget.Button[@text="입금확인"]')
                    deposit_check_btn.click()
                    time.sleep(1)
                    
                    popup_confirm_xpath = '//androidx.compose.ui.viewinterop.ViewFactoryHolder/android.webkit.WebView/android.webkit.WebView/android.view.View/android.app.AlertDialog//android.widget.Button[@text="확인"]'
                    WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((AppiumBy.XPATH, popup_confirm_xpath))
                    ).click()
                    time.sleep(2)
                except Exception:
                    pass

                try:
                    balance_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((AppiumBy.XPATH, balance_xpath))
                    )
                    numbers_only = re.sub(r'[^0-9]', '', balance_element.text)
                    balance = int(numbers_only) if numbers_only else 0
                except Exception:
                    pass

                if balance >= 10000:
                    break

        if balance < 10000:
            print("[테스트 종료] 잔액 부족으로 인한 투자 진행 불가")
            return False
        else:
            print("[성공] 예치금 1만원 이상 검증 통과!")
            
            # --------------------------------------------------------------------
            # [순수 해상도 비율 탭 & Y 좌표 자동 탐색 루프 (0.86 ~ 0.90)]
            # --------------------------------------------------------------------
            target_units = min(balance // 10000, 500)
            input_value = str(target_units)
            
            print(f"💰 계산된 입력값: '{input_value}' (순수 해상도 비율 좌표 계산 시작)")
            
            window_size = driver.get_window_size()
            screen_width = window_size['width']
            screen_height = window_size['height']
            
            key_ratios = {
                '1': (0.2, 0.68), '2': (0.5, 0.68), '3': (0.8, 0.68),
                '4': (0.2, 0.76), '5': (0.5, 0.76), '6': (0.8, 0.76),
                '7': (0.2, 0.84), '8': (0.5, 0.84), '9': (0.8, 0.84),
                '0': (0.5, 0.92)
            }
            
            amount_input = wait.until(
                EC.element_to_be_clickable((AppiumBy.XPATH, '//android.widget.EditText[@resource-id="id-amount"]'))
            )
            amount_input.click()
            time.sleep(1.5)
            
            for char in input_value:
                if char in key_ratios:
                    ratio_x, ratio_y = key_ratios[char]
                    target_x = int(screen_width * ratio_x)
                    target_y = int(screen_height * ratio_y)
                    
                    driver.tap([(target_x, target_y)], 100)
                    time.sleep(0.4)
                    
            time.sleep(0.5)
            
            # Y 좌표 자동 탐색 루프
            y_ratios_to_try = [0.86, 0.88, 0.90]
            confirm_success = False

            for y_ratio in y_ratios_to_try:
                conf_x = int(screen_width * 0.8)
                conf_y = int(screen_height * y_ratio)
                
                actions = ActionChains(driver)
                actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
                actions.w3c_actions.pointer_action.move_to_location(conf_x, conf_y)
                actions.w3c_actions.pointer_action.pointer_down()
                actions.w3c_actions.pointer_action.pause(0.3)
                actions.w3c_actions.pointer_action.pointer_up()
                actions.perform()
                
                try:
                    WebDriverWait(driver, 1.5).until(
                        EC.invisibility_of_element_located((AppiumBy.XPATH, '//android.app.AlertDialog[@resource-id="inputAmount"]'))
                    )
                    print(f"✅ [성공] Y 비율 {y_ratio} 지점에서 확인 버튼 인식 완료!")
                    confirm_success = True
                    break
                except Exception:
                    time.sleep(0.5)

            if not confirm_success:
                raise AssertionError("버그 검출: 모든 Y 좌표(0.86~0.90)에서 확인 버튼 탭이 실패했습니다.")
                
            time.sleep(1.0)
            
            # '투자하기' 버튼 가시성 검증 및 미노출 시 복구(Fallback) 로직
            target_btn_xpath = '//android.widget.Button[contains(@text, "개 상품에 투자하기") or contains(@text, "투자하기")]'
            
            try:
                print("🔍 '투자하기' 버튼이 화면에 정상 노출되는지 확인 중...")
                final_invest_btn = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((AppiumBy.XPATH, target_btn_xpath))
                )
                print("✅ [성공] '투자하기' 버튼 가시성 확인 완료!")
            except Exception:
                print("⚠️ [알림] '투자하기' 버튼이 즉시 보이지 않습니다. '투자금액 설정 닫기'를 통한 복구 로직을 실행합니다.")
                try:
                    close_setting_btn = driver.find_element(AppiumBy.XPATH, '//android.widget.Button[@content-desc="투자금액 설정 닫기"]')
                    close_setting_btn.click()
                    print("🔄 '투자금액 설정 닫기' 버튼 클릭 성공")
                    time.sleep(1.0)
                except Exception as close_err:
                    print(f"[참고] 닫기 버튼 탐색 실패 혹은 이미 닫힘: {close_err}")
                
                try:
                    re_active_btn = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((AppiumBy.XPATH, '//android.widget.Button[contains(@text, "개 상품 투자금액 설정하기")]'))
                    )
                    re_active_btn.click()
                    time.sleep(1.5)
                except Exception:
                    pass
                
                final_invest_btn = wait.until(
                    EC.element_to_be_clickable((AppiumBy.XPATH, target_btn_xpath))
                )
                
            final_invest_btn.click()
            print("🚀 최종 '투자하기' 버튼 클릭 완료!")
            time.sleep(3.0)
            
            # --------------------------------------------------------------------
            # [개선] 투자 동의 화면: 불필요한 중복 스크롤 제거 및 안정적인 id-agree 탐색
            # --------------------------------------------------------------------
            print("📜 투자 동의 화면: 필수 약관 체크 및 '동의함' 입력 진행 중...")
            
            try:
                scroll_disclosure = (
                    'new UiScrollable(new UiSelector().scrollable(true))'
                    '.scrollIntoView(new UiSelector().text("공시지표 확인 [필수]"))'
                )
                driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, scroll_disclosure).click()
                time.sleep(0.5)
            except Exception:
                pass

            try:
                scroll_terms = (
                    'new UiScrollable(new UiSelector().scrollable(true))'
                    '.scrollIntoView(new UiSelector().text("연계투자약관 확인 [필수]"))'
                )
                driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, scroll_terms).click()
                time.sleep(0.5)
            except Exception:
                pass

            # [핵심 수정] 불필요한 스크롤 코드를 제거하고, 바로 '동의함' 입력 필드 유연하게 탐색 후 입력
            try:
                print("🔍 '동의함' 입력 필드(`id-agree`) 대기 및 입력 중...")
                agree_input_field = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((AppiumBy.XPATH, '//android.widget.EditText[contains(@resource-id, "id-agree")]'))
                )
                agree_input_field.click()
                agree_input_field.clear()
                agree_input_field.send_keys("동의함")
                print("✅ '동의함' 텍스트 입력 완료!")
                time.sleep(1.0)
            except Exception as e:
                print(f"⚠️ 입력 필드 즉시 탐색 실패, 가벼운 스크롤 후 재시도: {e}")
                try:
                    scroll_input_simple = (
                        'new UiScrollable(new UiSelector().scrollable(true))'
                        '.scrollIntoView(new UiSelector().resourceIdMatches(".*id-agree.*"))'
                    )
                    driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, scroll_input_simple)
                    agree_input_field = wait.until(
                        EC.element_to_be_clickable((AppiumBy.XPATH, '//android.widget.EditText[contains(@resource-id, "id-agree")]'))
                    )
                    agree_input_field.click()
                    agree_input_field.clear()
                    agree_input_field.send_keys("동의함")
                    print("✅ 스크롤 후 '동의함' 텍스트 입력 완료!")
                except Exception as ex:
                    raise AssertionError(f"버그 검출: '동의함' 입력 필드를 찾거나 입력할 수 없습니다. 원인: {ex}")

            try:
                scroll_final_btn = (
                    'new UiScrollable(new UiSelector().scrollable(true))'
                    '.scrollIntoView(new UiSelector().text("위 내용에 모두 동의 합니다."))'
                )
                driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, scroll_final_btn)
                
                final_agree_btn = wait.until(
                    EC.element_to_be_clickable((AppiumBy.XPATH, '//android.widget.Button[@text="위 내용에 모두 동의 합니다."]'))
                )
                final_agree_btn.click()
                print("🚀 '위 내용에 모두 동의 합니다.' 버튼 클릭 성공! 최종 투자 신청 완료.")
                time.sleep(3.0)
            except Exception as e:
                raise e

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