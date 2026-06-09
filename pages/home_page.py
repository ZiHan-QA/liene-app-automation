from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class HomePage(BasePage):
    """Liene Photo APP 首页"""

    # ── 元素定位（按需补充）──────────────────────────────
    # 底部 Tab（Perilla 5个Tab / 其他机型 2个Tab）
    TAB_HOME = (AppiumBy.ACCESSIBILITY_ID, "首页")
    TAB_USER = (AppiumBy.ACCESSIBILITY_ID, "用户中心")

    def is_loaded(self) -> bool:
        """判断首页是否加载完成"""
        return self.is_visible(*self.TAB_USER, timeout=10)

    def go_to_user_center(self):
        self.tap(*self.TAB_USER)
        return self

    def get_current_activity(self) -> str:
        return self.driver.current_activity
