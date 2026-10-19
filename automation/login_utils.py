from playwright.sync_api import sync_playwright
import os


# 1. 순수 로그인 부품 함수만 덩그러니 있어야 합니다.
def test_moneymove_login(page):
  USER_ID = os.getenv("MONEYMOVE_ID")
  USER_PW = os.getenv("MONEYMOVE_PW")

  page.goto("https://moneymove.ai/")
  page.get_by_text("로그인").first.click()

  page.locator("#userId").fill(USER_ID)
  page.locator("#loginPassword").fill(USER_PW)
  page.locator("button[onclick*='loginConfirm']").click()

  try:
    error_popup = page.locator("#alertPopup")
    my_page_btn = page.locator("a.btn-gnb[href*='/invest/my-page/main']")

    if error_popup.is_visible(timeout=3000):
      print("❌ 로그인 실패")
      return False
    elif my_page_btn.is_visible(timeout=5000):
      print("로그인 성공")

      #투자 시작하기 버튼 찾기     
      invest_start_btn = page.get_by_text("투자 시작하기")

      # 버튼이 화면에 나타날 때까지 잠시 기다렸다가 클릭
      invest_start_btn.click()
      print("투자 페이지 진입 중.")

      # (참고) 페이지가 전환되는 동안 살짝 대기하거나 다음 요소가 나타나길 기다릴 수 있습니다.
      page.wait_for_load_state("networkidle")
    return True
  except:
    return False
