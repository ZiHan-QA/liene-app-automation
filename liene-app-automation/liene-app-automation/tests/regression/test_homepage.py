import pytest
from pages.home_page import HomePage


@pytest.mark.regression
def test_homepage_tab_visible(android_driver):
    """回归 - 底部 Tab 用户中心可见"""
    page = HomePage(android_driver)
    page.wait_seconds(3)
    assert page.is_visible(*HomePage.TAB_USER), "用户中心 Tab 不可见"
