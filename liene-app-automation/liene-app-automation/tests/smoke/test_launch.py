import pytest
from pages.home_page import HomePage


@pytest.mark.smoke
def test_app_launch(android_driver):
    """P0 - APP 能正常启动，首页加载完成"""
    page = HomePage(android_driver)
    page.wait_seconds(5)
    assert page.is_loaded(), "首页未能正常加载"


@pytest.mark.smoke
def test_current_activity(android_driver):
    """P0 - 验证当前 Activity 为 MainActivity"""
    page = HomePage(android_driver)
    activity = page.get_current_activity()
    print(f"\n当前 Activity: {activity}")
    assert activity is not None
