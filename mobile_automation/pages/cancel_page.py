import os
import time
import re
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .base_page import BasePage

class CancelPage(BasePage):
    def cancel_investment(self, captured_bond_text, initial_balance):
        # 1. 내 원리금수취권 진입
        try:
            self.scroll_into_view_by_text("내 원리금수취권 확인하기")
            self.click((AppiumBy.XPATH, '//android.widget.Button[@text="내 원리금수취권 확인하기"]'))
            time.sleep(2)
        except Exception as e:
            raise AssertionError(f"버그 검출: '내 원리금수취권 확인하기' 진입 실패: {e}")

        try:
            self.click((AppiumBy.XPATH, '(//android.widget.Button[@content-desc="상세보기 바로가기"])[1]'))
            time.sleep(2.5)
        except Exception as e:
            raise AssertionError(f"버그 검출: 원리금수취권 상세 화면 진입 실패: {e}")

        # 2. 채권 번호 검증
        try:
            detail_element = self.scroll_into_view_by_text(captured_bond_text)
            if detail_element.text != captured_bond_text:
                raise AssertionError(f"채권 번호 불일치! 투자 전({captured_bond_text}) != 상세({detail_element.text})")
        except Exception as e:
            raise AssertionError(f"버그 검출: 상세 화면 채권 번호 검증 실패: {e}")

        # 3. '투자취소' 버튼 클릭
        try:
            cancel_btn = None
            for _ in range(4):
                try:
                    btn = self.driver.find_element(AppiumBy.XPATH, '//android.widget.Button[@text="투자취소"]')
                    if btn.is_displayed():
                        cancel_btn = btn
                        break
                except Exception:
                    pass
                self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiScrollable(new UiSelector().scrollable(true)).scrollForward()')
                time.sleep(1)
            
            if not cancel_btn:
                raise TimeoutException("'투자취소' 버튼을 찾지 못했습니다.")
            cancel_btn.click()
            time.sleep(2.0)
        except Exception as e:
            raise AssertionError(f"버그 검출: '투자취소' 버튼 클릭 실패: {e}")

        # 4. 서명 입력 및 제출
        try:
            member_name = os.getenv('MEMBER_NAME', '홍길동')
            sign_field = self.type_text((AppiumBy.XPATH, '//android.widget.EditText[contains(@resource-id, "id-sign")]'), member_name)
            time.sleep(0.5)
            try:
                self.driver.hide_keyboard()
                time.sleep(1)
            except Exception:
                pass
        except Exception as e:
            raise AssertionError(f"버그 검출: 서명 입력 실패: {e}")

        try:
            print("🔍 서명 입력 후 취소 요청 제출 '확인' 버튼 클릭 중...")
            self.click((AppiumBy.XPATH, '(//android.widget.Button[@text="확인"])[last()]'))
            time.sleep(2)
        except Exception as e:
            raise AssertionError(f"버그 검출: 취소 요청 제출 버튼 클릭 실패: {e}")

        # 5. [핵심] 취소 완료 팝업 확인 버튼 정밀 클릭
        try:
            print("🔍 [취소 완료 화면] 팝업의 확인 버튼 정밀 대기 및 클릭 중...")
            completion_xpath = '//android.app.AlertDialog//android.widget.Button[@text="확인"] | (//*[contains(@text, "확인")])[last()]'
            self.click((AppiumBy.XPATH, completion_xpath))
            print("🚀 [성공] 취소 완료 화면의 '확인' 버튼 정밀 클릭 완료!")
            time.sleep(3)
        except Exception as e:
            raise AssertionError(f"버그 검출: 취소 완료 화면의 '확인' 버튼 클릭 실패: {e}")

        # 6. 잔액 정합성 검증 (정밀 타겟팅 경로 적용)
        print("🔍 취소 완료 후 예치금 잔액 복구 검증을 시작합니다...")
        try:
            self.driver.back()
            time.sleep(2.0)

            self.click((AppiumBy.XPATH, '//android.view.View[@text="내 투자"]'))
            print("✅ '내 투자' 메뉴 진입 성공")
            time.sleep(2)

            precise_balance_xpath = '//android.view.View[@resource-id="wrap"]/android.view.View[2]/android.view.View[2]/android.view.View[6]//android.view.View[contains(@text, "원") or contains(@text, ",")]'
            
            balance_el = self.wait.until(EC.presence_of_element_located((AppiumBy.XPATH, precise_balance_xpath)))
            final_numbers = re.sub(r'[^0-9]', '', balance_el.text)
            final_balance = int(final_numbers) if final_numbers else 0

            print(f"[비교 결과] 최초 잔액: {initial_balance:,}원 vs 취소 후 잔액: {final_balance:,}원")

            if initial_balance == final_balance:
                print("✨ [검증 성공] 투자 취소 후 예치금 잔액이 최초 금액과 정확히 일치합니다!")
            else:
                raise AssertionError(f"잔액 정합성 오류! 초기 잔액({initial_balance:,}원) != 취소 후 잔액({final_balance:,}원)")
        except Exception as err:
            raise AssertionError(f"버그 검출: 잔액 복구 검증 과정 오류: {err}")