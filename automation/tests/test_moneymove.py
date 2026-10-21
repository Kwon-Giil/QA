import os
import time
from dotenv import load_dotenv
from utils import secure_input

# 환경변수 불러오기
load_dotenv()
USER_ID = os.getenv("MONEYMOVE_ID")
USER_PW = os.getenv("MONEYMOVE_PW")
MEMBER_NAME = os.getenv("MONEYMOVE_MEMBER_NAME")


def test_moneymove_e2e_flow(page):
    """로그인 보안우회부터 프레시 쿼리, 삼중 정합성 검증, 최종 취소까지의 전체 E2E 사이클"""
    
    print("🚀 moneymove.ai 접속 및 로그인 진행 중...")
    page.goto("https://moneymove.ai/")

    try:
        # 1. 로그인 수행
        page.get_by_text("로그인").first.click()
        
        secure_input(page, "#userId", USER_ID)
        secure_input(page, "#loginPassword", USER_PW)
        
        page.locator("button[onclick*='loginConfirm']").click()
        print("🚀 로그인 버튼 클릭 완료!")

        # 2. 로그인 성공 검증 및 '투자 시작하기' 연계 동작
        error_popup = page.locator("#alertPopup")
        business_hours_notice = page.get_by_text("영업 시간")
        my_page_btn = page.locator("a.btn-gnb[href*='/invest/my-page/main']")

        if error_popup.is_visible(timeout=3000):
            fail_title = page.locator("#alert-title").inner_text()
            fail_contents = page.locator("#alert-contents").inner_text()
            raise Exception(f"로그인 실패 팝업 감지: [{fail_title}] {fail_contents}")

        elif business_hours_notice.is_visible(timeout=2000):
            raise Exception("영업 시간이 아닙니다.")

        elif my_page_btn.is_visible(timeout=5000):
            print("[LOGIN SUCCESS] 로그인 성공! 마이페이지 진입 완료.")
            print("'투자 시작하기' 버튼을 찾는 중...")
            page.get_by_text("투자 시작하기").first.click()
            print("👉 투자 페이지 진입 완료.")
        else:
            raise Exception("로그인 상태를 확인할 수 없습니다.")

        # 3. [실시간 프레시 쿼리] 상품 목록 확인 및 Graceful Exit 반영
        print("⏳ 투자 가능 상품 셀 로딩 대기 중...")
        
        try:
            target_td = page.locator("td.data-check").first
            target_td.wait_for(state="visible", timeout=10000)
        except Exception:
            print("⚠️ [GRACEFUL EXIT] 투자 가능한 상품(모집 중)이 없습니다. 테스트를 안전하게 종료합니다.")
            return

        # 4. 내부 input 요소에서 오늘의 티켓 번호(id) 실시간 동적 추출
        checkbox_input = target_td.locator("input.js_list-item")
        selected_bond_id = checkbox_input.get_attribute("id")

        if not selected_bond_id or not selected_bond_id.startswith("TK_"):
            raise Exception(f"[ERROR] 유효한 티켓 번호 추출 실패: {selected_bond_id}")

        print(f"📌 [1단계 정합성 타겟 - 실시간 추출] 오늘의 티켓 번호: {selected_bond_id}")

        # 5. 상품 선택
        try:
            target_td.locator("label.loan-check").click(force=True)
        except Exception:
            print("⚠️ [GRACEFUL EXIT] 상품이 실시간으로 마감되어 선택할 수 없습니다. 테스트를 안전하게 종료합니다.")
            return

        time.sleep(1)

        panel_open_btn = page.locator("button.btn-product-panel[data-mode='open']")
        if panel_open_btn.is_visible(timeout=2000):
            print("📂 바텀시트 패널 열기 클릭")
            panel_open_btn.click()
            time.sleep(1)
        
        print("👉 첫 번째 상품 선택 및 패널 열기 완료!")

        # 6. 예치금 잔액 확인 및 가상계좌 동기화 폴링
        amount_elem = page.locator("#js_available-fund-amount")
        amount_elem.wait_for(state="visible", timeout=3000)
        clean_amount = int(amount_elem.inner_text().replace(",", "") or 0)
        print(f"💰 최초 확인된 예치금 잔액: {clean_amount:,}원")

        if clean_amount < 10000:
            print("⚠️ [INFO] 예치금이 부족합니다. 가상계좌 입금 내역 동기화를 시도합니다.")
            sync_btn = page.locator("#syncVirtualAccount")
            max_retries = 5
            
            for attempt in range(1, max_retries + 1):
                if sync_btn.is_visible():
                    sync_btn.scroll_into_view_if_needed()
                    print(f"🔄 [시도 {attempt}/{max_retries}] '입금확인' 버튼 클릭 및 반영 대기 중...")
                    sync_btn.click()
                    page.wait_for_timeout(3000)
                    
                    clean_amount = int(amount_elem.inner_text().replace(",", "") or 0)
                    print(f"💰 현재 예치금 잔액: {clean_amount:,}원")
                    
                    if clean_amount >= 10000:
                        print("✨ 잔액 서버 반영 완료!")
                        break
                
                if attempt < max_retries:
                    page.wait_for_timeout(2000)

        if clean_amount < 10000:
            print(f"⚠️ [GRACEFUL EXIT] 동기화 후에도 예치금이 {clean_amount:,}원으로 10,000원 미만입니다. 테스트 종료.")
            return

        # 7. 투자 금액 산정 및 입력
        MAX_GENERAL_INVESTOR_LIMIT = 5000000
        target_amount = min(clean_amount, MAX_GENERAL_INVESTOR_LIMIT)
        input_value = int(target_amount // 10000)
        print(f"📊 [CALCULATION] 투자 대상 금액: {target_amount:,}원 (입력값: {input_value}만원)")

        amount_input = page.locator("input.js_invest-amount").first
        amount_input.wait_for(state="visible", timeout=3000)
        amount_input.fill(str(input_value))
        amount_input.press("Tab")
        time.sleep(0.5)

        page.locator("#js_next-process").first.click()
        print("🎉 '투자하기' 버튼 클릭 완료!")

        # 8. [2단계 정합성 검사] 동의 화면 (td.data-code 활용)
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        consent_bond_elem = page.locator("td.data-code").first
        consent_bond_elem.wait_for(state="visible", timeout=5000)
        consent_bond_id = consent_bond_elem.inner_text().strip()

        if consent_bond_id != selected_bond_id:
            raise Exception(f"[INTEGRITY ERROR] 2단계 검증 실패! 1번({selected_bond_id})과 동의 화면 번호({consent_bond_id}) 불일치")
        print(f"✅ [2단계 정합성 통과] 티켓 번호 일치 확인: {consent_bond_id}")

        # 공시지표 동의 및 서명
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)

        disclosure_label = page.locator("label[for='chk1']")
        disclosure_label.wait_for(state="visible", timeout=3000)
        disclosure_label.scroll_into_view_if_needed()
        disclosure_label.click()
        time.sleep(0.5)

        sign_input = page.locator("#js_sign-input")
        sign_input.wait_for(state="visible", timeout=3000)
        sign_input.scroll_into_view_if_needed()
        sign_input.click()
        sign_input.fill("동의함")
        sign_input.press("Tab")
        time.sleep(0.5)

        page.locator("#js_next-process").click()
        print("🚀 최종 투자 동의 완료!")

        # 9. [3단계 최종 정합성 검사] 원리금수취권 목록
        page.get_by_text("내 원리금수취권 확인하기").wait_for(state="visible", timeout=5000)
        page.get_by_text("내 원리금수취권 확인하기").click()
        time.sleep(2)

        fundraising_tab = page.locator("#fundraising")
        fundraising_tab.wait_for(state="visible", timeout=3000)
        fundraising_tab.click()
        time.sleep(2)

        final_bond_elem = page.locator("td.data-code").first
        final_bond_elem.wait_for(state="visible", timeout=5000)
        final_bond_id = final_bond_elem.inner_text().strip()

        if final_bond_id != selected_bond_id:
            raise Exception(f"[INTEGRITY ERROR] 3단계 최종 검증 실패! 원본({selected_bond_id})과 목록 번호({final_bond_id}) 불일치")
        print(f"✨ [3단계 정합성 검증 완료] 1번 == 2번 == 3번 ({final_bond_id}) 완벽 일치!")

        # 10. [투자 취소 프로세스]
        print("🗑️ 투자 취소 대상 채권을 선택합니다.")
        target_row = page.locator("tr", has_text=selected_bond_id).first
        target_row.wait_for(state="visible", timeout=5000)

        target_row.locator("label[for^='IC_']").first.scroll_into_view_if_needed()
        target_row.locator("label[for^='IC_']").first.click()
        time.sleep(0.5)

        page.locator("#invest_cancel").wait_for(state="visible", timeout=3000)
        page.locator("#invest_cancel").click()

        print("✍️ 취소 확인 팝업 내 서명을 입력합니다.")
        cancel_input = page.locator("#cancel-autogragh-input")
        cancel_input.wait_for(state="visible", timeout=3000)
        cancel_input.fill(MEMBER_NAME)
        cancel_input.press("Tab")
        time.sleep(0.5)

        page.locator("#contract-button").wait_for(state="visible", timeout=3000)
        page.locator("#contract-button").click()

        alert_msg = page.locator("#alert-contents")
        alert_msg.wait_for(state="visible", timeout=3000)
        msg_text = alert_msg.inner_text().strip()
        print(f"📢 팝업 메시지 확인: {msg_text}")

        assert "투자취소가 완료되었습니다" in msg_text, f"[ERROR] 취소 완료 메시지 불일치: {msg_text}"
        print("🏆 모든 E2E 사이클 Pytest 모듈화 실행 성공!")

    except Exception as e:
        print(f"[CRITICAL ERROR] 예외 발생: {e}")
        page.screenshot(path="screenshots/investment_error_debug.png", full_page=True)
        raise e