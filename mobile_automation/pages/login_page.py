import os
import time
from appium.webdriver.common.appiumby import AppiumBy
from .base_page import BasePage

class LoginPage(BasePage):
    def login_with_pin(self):
        pin_str = os.getenv('PIN', '123456')
        print(f"🔐 핀 번호 입력 시작 (총 {len(pin_str)}자리)...")
        
        for digit in pin_str:
            self.click((AppiumBy.XPATH, f'//*[@text="{digit}"]'))
            time.sleep(0.3)
            
        print("✨ 핀 번호 입력이 완료되었습니다!")
        time.sleep(3)