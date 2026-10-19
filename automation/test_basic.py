from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os
import time

# 환경변수 불러오기
load_dotenv()
USER_ID = os.getenv("MONEYMOVE_ID")
USER_PW = os.getenv("MONEYMOVE_PW")

with sync_playwright() as p:
    # 1. 브라우저 창 최대화 실행 (고정 뷰포트 해제 및 최대화 인자 전달)
    browser = p.chromium.launch(headless=False, args=["--start-maximized"])
    page = browser.new_page(no_viewport=True)

    print("🚀 moneymove.ai 접속 및 로그인 진행 중...")
    page.goto("https://moneymove.ai/")

    try:
        # 2. 로그인 수행
        page.get_by_text("로그인").first.click()
        page.locator("#userId").fill(USER_ID)
        page.locator("#loginPassword").fill(USER_PW)
        page.locator("button[onclick*='loginConfirm']").click()

        # 3. 로그인 성공 검증 및 '투자 시작하기' 연계 동작
        error_popup = page.locator("#alertPopup")
        business_hours_notice = page.get_by_text("영업 시간")
        my_page_btn = page.locator("a.btn-gnb[href*='/invest/my-page/main']")

        if error_popup.is_visible(timeout=3000):
            fail_title = page.locator("#alert-title").inner_text()
            fail_contents = page.locator("#alert-contents").inner_text()
            print(f"[LOGIN FAIL] 로그인 실패: [{fail_title}] {fail_contents}")
            raise Exception(f"로그인 실패: {fail_title}")

        elif business_hours_notice.is_visible(timeout=2000):
            print("[TIME RESTRICTION] 영업 시간이 아닙니다.")
            raise Exception("영업 시간 아님")

        elif my_page_btn.is_visible(timeout=5000):
            print("[LOGIN SUCCESS] 로그인 성공! 마이페이지 진입 완료.")

            # 4. 로그인 직후 '투자 시작하기' 버튼 클릭
            print("'투자 시작하기' 버튼을 찾는 중...")
            invest_start_btn = page.get_by_text("투자 시작하기").first
            invest_start_btn.click()
            print("'투자 시작하기' 버튼 클릭 완료! 투자 페이지로 진입했습니다.")

        else:
            print("[WARNING] 팝업도 안 뜨고 마이페이지도 제때 안 나타남")
            raise Exception("로그인 상태 확인 불가")

        # 5. 투자 상품 목록 확인 및 선택
        print("🔍 투자 상품 목록 확인 중...")
        time.sleep(2)  # DOM 안정화 대기
        product_checkboxes = page.locator("input.js_list-item")
        product_count = product_checkboxes.count()

        if product_count == 0:
            print("⚠️ [GRACEFUL EXIT] 투자 가능 상품 없음. 테스트를 안전하게 종료합니다.")
        else:
            print(f"✅ [SUCCESS] 총 {product_count}개의 투자 상품을 발견했습니다! 첫 번째 상품을 선택합니다.")
            
            # 💡 [1단계 정합성 타겟] 첫 번째 상품의 채권 번호 추출 (기준점 1번)
            bond_number_elem = page.locator("span.data-info.ticket-number").first
            bond_number_elem.wait_for(state="visible", timeout=3000)
            selected_bond_id = bond_number_elem.inner_text().strip()
            print(f"📌 [1단계 정합성 타겟] 선택한 상품 채권 번호: {selected_bond_id}")

            # 포인터 인터셉션 방지를 위해 label 클릭
            page.locator("label.loan-check").first.click()
            time.sleep(1)

            # 바텀시트 패널이 접혀있는 경우 열기 버튼 강제 클릭
            panel_open_btn = page.locator("button.btn-product-panel[data-mode='open']")
            if panel_open_btn.is_visible(timeout=2000):
                print("📂 바텀시트 패널이 닫혀 있어 열기 버튼을 클릭합니다.")
                panel_open_btn.click()
                time.sleep(1)
            
            print("👉 첫 번째 상품 선택 및 패널 열기 완료!")

            # 6. 실제 예치금 잔액 요소 가져오기 (#js_available-fund-amount)[cite: 1]
            amount_elem = page.locator("#js_available-fund-amount")
            amount_elem.wait_for(state="visible", timeout=3000)
            amount_text = amount_elem.inner_text().strip()
            clean_amount = int(amount_text.replace(",", "") or 0)
            print(f"💰 최초 확인된 예치금 잔액: {clean_amount:,}원")

            # 7. 10,000원 미만일 경우 가상계좌 동기화 및 재시도 폴링(Retry Polling) 시작
            if clean_amount < 10000:
                print(f"⚠️ [INFO] 예치금이 부족합니다. 입금 내역 서버 반영 및 동기화를 시도합니다.")
                
                sync_btn = page.locator("#syncVirtualAccount")
                max_retries = 5  # 최대 5번 시도 (서버 반영 대기)
                
                for attempt in range(1, max_retries + 1):
                    if sync_btn.is_visible():
                        sync_btn.scroll_into_view_if_needed()
                        print(f"🔄 [시도 {attempt}/{max_retries}] '입금확인' 버튼 클릭 및 반영 대기 중...")
                        sync_btn.click()
                        time.sleep(1)
                        
                        page.wait_for_timeout(3000)
                        
                        updated_text = amount_elem.inner_text().strip()
                        clean_amount = int(updated_text.replace(",", "") or 0)
                        print(f"💰 현재 예치금 잔액: {clean_amount:,}원")
                        
                        if clean_amount >= 10000:
                            print("✨ 잔액 서버 반영 완료!")
                            break
                    
                    if attempt < max_retries:
                        print(f"⏳ 아직 잔액이 반영되지 않았습니다. 잠시 후 재시도합니다...")
                        page.wait_for_timeout(2000)

            # 8. 최종 예치금 잔액 검증
            if clean_amount < 10000:
                print(f"⚠️ [GRACEFUL EXIT] 동기화 후에도 예치금이 {clean_amount:,}원으로 10,000원 미만입니다. 테스트 종료.")
            else:
                print(f"🚀 투자 신청을 진행합니다.")
                
                # 일반 투자자 최대 한도 (500만 원) 및 만원 단위 버림 처리
                MAX_GENERAL_INVESTOR_LIMIT = 5000000
                target_amount = min(clean_amount, MAX_GENERAL_INVESTOR_LIMIT)
                input_value = int(target_amount // 10000)

                print(f"📊 [CALCULATION] 투자 대상 금액: {target_amount:,}원 (입력값: {input_value}만원)")

                # 금액 입력 필드에 값 주입 (Strict Mode 방지를 위해 .first 사용)
                amount_input = page.locator("input.js_invest-amount").first
                amount_input.wait_for(state="visible", timeout=3000)
                amount_input.fill(str(input_value))
                
                # Tab 키로 포커스 해제하여 유효성 검사 및 버튼 활성화 유도
                amount_input.press("Tab")
                time.sleep(0.5)
                print(f"✍️ 금액 입력 및 활성화 완료: {input_value}만원")
                
                # 첫 번째 '투자하기' 버튼 클릭
                invest_btn = page.locator("#js_next-process").first
                invest_btn.wait_for(state="visible", timeout=3000)
                invest_btn.click()
                print("🎉 '투자하기' 버튼 클릭 완료! 다음 페이지로 이동합니다.")

                # 10. 다음 페이지 진입 후 [2단계 정합성 검사] (동의 화면)
                print("📜 다음 페이지 로딩 대기 중...")
                page.wait_for_load_state("networkidle")
                time.sleep(1)

                # 💡 [2단계 검증] 동의 화면의 채권 번호와 1번 원본 번호 비교
                consent_bond_elem = page.locator("span.data-info.js_ticket-id").first
                consent_bond_elem.wait_for(state="visible", timeout=5000)
                consent_bond_id = consent_bond_elem.inner_text().strip()

                if consent_bond_id != selected_bond_id:
                    raise Exception(f"[INTEGRITY ERROR] 2단계 검증 실패! 1번({selected_bond_id})과 동의 화면 번호({consent_bond_id})가 일치하지 않습니다.")
                print(f"✅ [2단계 정합성 통과] 1번과 2번 채권 번호 일치 확인: {consent_bond_id}")

                # 하단 스크롤 및 필수 체크, 서명 입력
                print("📜 페이지 하단으로 스크롤을 이동합니다...")
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)

                print("☑️ '공시지표 확인 [필수]' 항목을 체크합니다.")
                disclosure_label = page.locator("label[for='chk1']")
                disclosure_label.wait_for(state="visible", timeout=3000)
                disclosure_label.scroll_into_view_if_needed()
                disclosure_label.click()
                time.sleep(0.5)

                print("✍️ 서명 입력란에 '동의함'을 입력합니다.")
                sign_input = page.locator("#js_sign-input")
                sign_input.wait_for(state="visible", timeout=3000)
                sign_input.scroll_into_view_if_needed()
                sign_input.click()
                sign_input.fill("동의함")
                sign_input.press("Tab")
                time.sleep(0.5)
                print("✨ 서명 입력 완료!")

                # 13. 최종 '투자 동의' 버튼 클릭
                print("🎉 최종 '투자 동의' 버튼을 클릭합니다.")
                final_consent_btn = page.locator("#js_next-process")
                final_consent_btn.wait_for(state="visible", timeout=3000)
                final_consent_btn.scroll_into_view_if_needed()
                final_consent_btn.click()
                print("🚀 투자 동의 완료!")

                # 14. '내 원리금수취권 확인하기' 버튼 클릭하여 메뉴 진입
                print("🔍 '내 원리금수취권 확인하기' 버튼을 클릭합니다.")
                my_bond_btn = page.get_by_text("내 원리금수취권 확인하기")
                my_bond_btn.wait_for(state="visible", timeout=5000)
                my_bond_btn.click()
                time.sleep(2)  # 페이지 이동 대기

                # 15. '모집 중' 탭(#fundraising) 클릭
                print("📂 '모집 중' 탭(#fundraising)을 클릭합니다.")
                fundraising_tab = page.locator("#fundraising")
                fundraising_tab.wait_for(state="visible", timeout=3000)
                fundraising_tab.click()
                time.sleep(2)  # 목록 렌더링 대기

                # 💡 [3단계 최종 정합성 검사] 원리금수취권 '모집 중' 목록의 채권 번호와 1번 원본 번호 비교
                final_bond_elem = page.locator("span.data-info.loan-number").first
                final_bond_elem.wait_for(state="visible", timeout=5000)
                final_bond_id = final_bond_elem.inner_text().strip()

                if final_bond_id != selected_bond_id:
                    raise Exception(f"[INTEGRITY ERROR] 3단계 최종 검증 실패! 1번 원본 번호({selected_bond_id})와 최종 원리금수취권 목록 번호({final_bond_id})가 일치하지 않습니다.")
                
                print(f"✨ [3단계 최종 정합성 검증 완료] 1번({selected_bond_id}) == 2번 == 3번({final_bond_id}) 완벽 일치 확인!")
                print("🏆 모든 E2E 자동화 및 삼중 정합성 검증 테스트가 완벽하게 성공했습니다!")

    except Exception as e:
        print(f"[CRITICAL ERROR] 예외 발생: {e}")
        page.screenshot(path="investment_error_debug.png", full_page=True)

    input("\n테스트가 완료되었습니다. 브라우저를 닫으려면 엔터를 누르세요...")
    browser.close()