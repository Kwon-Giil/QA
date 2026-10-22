def secure_input(page, selector, value):
    """보안 스크립트 및 합성 이벤트 차단을 우회하기 위해 JS로 직접 값을 주입하고 이벤트를 강제 트리거"""
    locator = page.locator(selector).first
    locator.wait_for(state="visible", timeout=5000)
    locator.click()
    
    page.evaluate(
        """([sel, val]) => {
            const el = document.querySelector(sel);
            if (el) {
                el.value = val;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }""",
        [selector, value]
    )
    print(f"보안 우회 주입 완료 [{selector}]")
