import time
import re
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions import interaction
from .base_page import BasePage

class InvestPage(BasePage):
    def check_sold_out(self):
        sold_out_xpath = '//android.view.View[@resource-id="wrap"]/android.view.View[2]/android.view.View[2]/android.view.View/android.view.View/android.view.View[2]//android.widget.TextView[@text="투자가 모두 마감되었습니다."]'
        try:
            self.wait.until(EC.presence_of_element_located((AppiumBy.XPATH, sold_out_xpath)))
            print("==========================================")
            print("[테스트 종료] 투자가 모두 마감되었습니다. 진행 가능한 상품이 없습니다.")
            print("==========================================")
            return True
        except Exception:
            print("투자 가능 상품 확인: 투자 테스트 시작")
            return False

    def select_first_product(self):
        print("🔍 첫 번째 상품의 '상세보기' 버튼 찾는 중...")
        self.click((AppiumBy.XPATH, '(//android.widget.Button[@content-desc="상세보기 바로가기"])[1]'))
        time.sleep(3)

    def get_bond_text(self):
        print("🔍 첫 번째 상품의 채권 번호(`TK_`) 찾는 중...")
        try:
            visible_bonds = self.driver.find_elements(AppiumBy.XPATH, '//*[starts-with(@text, "TK_")]')
            if visible_bonds:
                bond_text = visible_bonds[0].text
                print(f"[성공] 화면에 노출된 채권 번호 획득: {bond_text}")
                return bond_text
            else:
                bond_element = self.scroll_into_view_by_prefix("TK_")
                print(f"[성공] 스크롤하여 가져온 채권 번호: {bond_element.text}")
                return bond_element.text
        except Exception:
            print("[오류] 채권 번호 미출력")
            return "TK_UNKNOWN"

    def proceed_to_amount_setting(self):
        try:
            visible_select_btns = self.driver.find_elements(AppiumBy.XPATH, '//*[@text="상품 선택하기"]')
            if visible_select_btns:
                select_btn = visible_select_btns[0]
            else:
                select_btn = self.scroll_into_view_by_text("상품 선택하기")
            select_btn.click()
            time.sleep(3)
        except Exception as e:
            raise AssertionError(f"버그 검출: '상품 선택하기' 버튼 클릭 실패: {e}")

        try:
            active_btn = self.wait.until(
                EC.element_to_be_clickable((AppiumBy.XPATH, '//android.widget.Button[contains(@text, "개 상품 투자금액 설정하기")]'))
            )
            active_btn.click()
            time.sleep(2)
        except Exception as e:
            raise AssertionError(f"버그 검출: 투자 진행 버튼 활성화 실패: {e}")

    def verify_and_handle_balance(self):
        balance_xpath = '//android.app.AlertDialog/android.view.View[3]/android.widget.ListView[1]/android.view.View[4]//android.view.View[contains(@text, "원")]'
        balance = 0
        try:
            balance_element = self.wait.until(EC.presence_of_element_located((AppiumBy.XPATH, balance_xpath)))
            numbers_only = re.sub(r'[^0-9]', '', balance_element.text)
            balance = int(numbers_only) if numbers_only else 0
            print(f"[정보] 최초 확인된 예치금 잔액: {balance:,}원")
        except Exception:
            balance = 0

        initial_balance = balance

        if balance < 10000:
            print("[안내] 잔액이 1만원 미만입니다. 입금 확인 재시도를 시작합니다.")
            for _ in range(3):
                try:
                    self.click((AppiumBy.XPATH, '//android.widget.Button[@text="입금확인"]'))
                    time.sleep(1)
                    popup_confirm_xpath = '//androidx.compose.ui.viewinterop.ViewFactoryHolder/android.webkit.WebView/android.webkit.WebView/android.view.View/android.app.AlertDialog//android.widget.Button[@text="확인"]'
                    self.click((AppiumBy.XPATH, popup_confirm_xpath))
                    time.sleep(2)
                except Exception:
                    pass

                try:
                    balance_element = self.wait.until(EC.presence_of_element_located((AppiumBy.XPATH, balance_xpath)))
                    numbers_only = re.sub(r'[^0-9]', '', balance_element.text)
                    balance = int(numbers_only) if numbers_only else 0
                except Exception:
                    pass

                if balance >= 10000:
                    break

        if balance < 10000:
            raise AssertionError("테스트 종료: 잔액 부족으로 인한 투자 진행 불가")
        
        print("[성공] 예치금 1만원 이상 검증 통과!")
        return initial_balance, balance

    def enter_investment_amount(self, balance):
        target_units = min(balance // 10000, 500)
        input_value = str(target_units)
        
        window_size = self.driver.get_window_size()
        screen_width = window_size['width']
        screen_height = window_size['height']
        
        key_ratios = {
            '1': (0.2, 0.68), '2': (0.5, 0.68), '3': (0.8, 0.68),
            '4': (0.2, 0.76), '5': (0.5, 0.76), '6': (0.8, 0.76),
            '7': (0.2, 0.84), '8': (0.5, 0.84), '9': (0.8, 0.84),
            '0': (0.5, 0.92)
        }
        
        self.click((AppiumBy.XPATH, '//android.widget.EditText[@resource-id="id-amount"]'))
        time.sleep(1.5)
        
        for char in input_value:
            if char in key_ratios:
                rx, ry = key_ratios[char]
                self.driver.tap([(int(screen_width * rx), int(screen_height * ry))], 100)
                time.sleep(0.4)
                
        time.sleep(0.5)

        # 금액 설정 완료 확인 버튼 탭
        y_ratios_to_try = [0.86, 0.88, 0.90]
        confirm_success = False
        for y_ratio in y_ratios_to_try:
            cx, cy = int(screen_width * 0.8), int(screen_height * y_ratio)
            actions = ActionChains(self.driver)
            actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
            actions.w3c_actions.pointer_action.move_to_location(cx, cy)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.pause(0.3)
            actions.w3c_actions.pointer_action.pointer_up()
            actions.perform()
            
            try:
                self.wait.until(EC.invisibility_of_element_located((AppiumBy.XPATH, '//android.app.AlertDialog[@resource-id="inputAmount"]')))
                confirm_success = True
                break
            except Exception:
                time.sleep(0.5)

        if not confirm_success:
            raise AssertionError("버그 검출: 모든 Y 좌표에서 확인 버튼 탭이 실패했습니다.")
        time.sleep(1.0)

    def submit_final_investment(self):
        target_btn_xpath = '//android.widget.Button[contains(@text, "개 상품에 투자하기") or contains(@text, "투자하기")]'
        try:
            final_btn = self.wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, target_btn_xpath)))
        except Exception:
            try:
                self.click((AppiumBy.XPATH, '//android.widget.Button[@content-desc="투자금액 설정 닫기"]'))
                time.sleep(1.0)
            except Exception:
                pass
            try:
                self.click((AppiumBy.XPATH, '//android.widget.Button[contains(@text, "개 상품 투자금액 설정하기")]'))
                time.sleep(1.5)
            except Exception:
                pass
            final_btn = self.wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, target_btn_xpath)))
            
        final_btn.click()
        time.sleep(3.0)

    def handle_agreements_and_review(self):
        try:
            self.scroll_into_view_by_text("공시지표 확인 [필수]").click()
            time.sleep(0.5)
        except Exception:
            pass

        try:
            self.scroll_into_view_by_text("연계투자약관 확인 [필수]").click()
            time.sleep(0.5)
        except Exception:
            pass

        try:
            agree_input = self.wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, '//android.widget.EditText[contains(@resource-id, "id-agree")]')))
            agree_input.click()
            agree_input.clear()
            agree_input.send_keys("동의함")
            time.sleep(1.0)
        except Exception:
            self.scroll_into_view_by_text("위 내용에 모두 동의 합니다.")
            agree_input = self.wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, '//android.widget.EditText[contains(@resource-id, "id-agree")]')))
            agree_input.click()
            agree_input.clear()
            agree_input.send_keys("동의함")

        try:
            self.scroll_into_view_by_text("위 내용에 모두 동의 합니다.")
            self.click((AppiumBy.XPATH, '//android.widget.Button[@text="위 내용에 모두 동의 합니다."]'))
            time.sleep(3.0)
        except Exception as e:
            raise e

        # 리뷰 팝업 처리
        try:
            self.wait.until(EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.TextView[@text="투자자님들의 의견이 중요해요!"]')))
            self.click((AppiumBy.XPATH, '//android.view.ViewGroup/android.view.View/android.view.View/android.view.View/android.view.View[1]/android.widget.Button'))
            time.sleep(1.0)
        except Exception:
            pass