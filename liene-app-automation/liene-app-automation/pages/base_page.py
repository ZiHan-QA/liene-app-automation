from appium.webdriver.webdriver import WebDriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time


class BasePage:
    """所有页面对象的基类，封装常用操作"""

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout=15)

    # ── 元素查找 ──────────────────────────────────────────
    def find(self, by: str, value: str, timeout: int = 15):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def find_all(self, by: str, value: str):
        return self.driver.find_elements(by, value)

    def is_visible(self, by: str, value: str, timeout: int = 5) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
            return True
        except TimeoutException:
            return False

    # ── 操作 ──────────────────────────────────────────────
    def tap(self, by: str, value: str, timeout: int = 15):
        el = self.find(by, value, timeout)
        el.click()
        return self

    def input_text(self, by: str, value: str, text: str):
        el = self.find(by, value)
        el.clear()
        el.send_keys(text)
        return self

    def swipe_up(self, duration: int = 500):
        size = self.driver.get_window_size()
        x = size["width"] // 2
        start_y = int(size["height"] * 0.75)
        end_y = int(size["height"] * 0.25)
        self.driver.swipe(x, start_y, x, end_y, duration)

    def swipe_down(self, duration: int = 500):
        size = self.driver.get_window_size()
        x = size["width"] // 2
        start_y = int(size["height"] * 0.25)
        end_y = int(size["height"] * 0.75)
        self.driver.swipe(x, start_y, x, end_y, duration)

    def wait_seconds(self, sec: float):
        time.sleep(sec)
        return self

    # ── 截图 ──────────────────────────────────────────────
    def screenshot_base64(self) -> str:
        return self.driver.get_screenshot_as_base64()

    def screenshot_save(self, path: str):
        self.driver.get_screenshot_as_file(path)
