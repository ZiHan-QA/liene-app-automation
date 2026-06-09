"""
启动页多语言文案验证
验证流程（每种语言）：
  1. adb 切换系统语言
  2. 清除 APP 数据并重启（触发引导流程）
  3. 截图隐私协议弹窗 → DeepSeek 验证文案
  4. 点「同意」→ 处理通知权限弹窗
  5. 截图引导页 → DeepSeek 验证文案
  6. 点「下一步」→ 截图国家选择页 → DeepSeek 验证文案
"""
import pytest
import allure
import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException

from lang_config import LANGUAGES
from copy_client import get_copy_for_lang
from ai_assert.vision_assert import assert_copy_by_vision
from adb_lang import restart_app_with_lang
from pages.base_page import BasePage


# ── 元素定位（按实际 resource-id 调整）──
BTN_AGREE      = (AppiumBy.XPATH, '//*[@text="同意" or @text="Agree" or contains(@resource-id,"agree")]')
BTN_DISAGREE   = (AppiumBy.XPATH, '//*[@text="不同意并退出" or contains(@resource-id,"disagree")]')
BTN_ALLOW      = (AppiumBy.XPATH, '//*[@text="允许" or @text="Allow" or contains(@resource-id,"allow")]')
BTN_DENY       = (AppiumBy.XPATH, '//*[@text="禁止" or @text="Deny" or contains(@resource-id,"deny")]')
BTN_NEXT       = (AppiumBy.XPATH, '//*[@text="下一步" or @text="Next" or contains(@resource-id,"next")]')
BTN_SURE       = (AppiumBy.XPATH, '//*[@text="确定" or @text="Confirm" or contains(@resource-id,"sure") or contains(@resource-id,"confirm")]')
PRIVACY_DIALOG = (AppiumBy.XPATH, '//*[contains(@resource-id,"alert") or contains(@resource-id,"dialog") or contains(@resource-id,"privacy")]')
GUIDE_PAGE     = (AppiumBy.XPATH, '//*[contains(@resource-id,"guide") or contains(@resource-id,"onboard")]')
COUNTRY_PAGE   = (AppiumBy.XPATH, '//*[contains(@resource-id,"country") or contains(@resource-id,"region")]')


def handle_notification_permission(page: BasePage):
    """处理系统通知权限弹窗（如果出现）"""
    try:
        if page.is_visible(*BTN_ALLOW, timeout=3):
            page.tap(*BTN_ALLOW)
            time.sleep(1)
    except Exception:
        pass


def make_test_id(lang: dict) -> str:
    return f"{lang['lang_code']}_{lang['display_name']}"


# 用 parametrize 生成 17 个语言的用例
@pytest.mark.parametrize("lang", LANGUAGES, ids=[make_test_id(l) for l in LANGUAGES])
@pytest.mark.smoke
@pytest.mark.splash
@allure.feature("启动页多语言验证")
def test_splash_i18n(android_driver, lang):
    """启动页 - 多语言文案验证（隐私弹窗 + 引导页 + 国家选择页）"""

    lang_code    = lang["lang_code"]
    lang_locale  = lang["android_locale"]
    lang_name    = lang["display_name"]
    page = BasePage(android_driver)

    allure.dynamic.title(f"启动页文案验证 - {lang_name}")

    # ── Step 1: 切换语言，清数据重启 APP ──
    with allure.step(f"切换系统语言为 {lang_name}，重启 APP"):
        restart_app_with_lang(lang_locale, clear_data=True)
        page.wait_seconds(3)

    # ── Step 2: 隐私协议弹窗验证 ──
    with allure.step("验证隐私协议弹窗文案"):
        if page.is_visible(*BTN_AGREE, timeout=5):
            # 拉取预期文案
            privacy_copy = get_copy_for_lang("splash", lang_code)
            # 只取弹窗相关 key（alert_ 开头 + btn_agree/disagree）
            dialog_copy = {k: v for k, v in privacy_copy.items()
                          if k.startswith("alert") or k in ("btn_agree", "btn_disagree", "btn_sure")}

            # 截图
            screenshot = android_driver.get_screenshot_as_base64()
            allure.attach(
                android_driver.get_screenshot_as_png(),
                name=f"隐私弹窗_{lang_name}",
                attachment_type=allure.attachment_type.PNG
            )

            # AI 视觉断言
            result = assert_copy_by_vision(
                screenshot_base64=screenshot,
                lang_display_name=lang_name,
                expected_copy=dialog_copy,
                page_desc="隐私协议弹窗"
            )
            allure.attach(
                str(result),
                name=f"断言结果_{lang_name}_隐私弹窗",
                attachment_type=allure.attachment_type.TEXT
            )
            assert result["result"] != "fail", \
                f"[{lang_name}] 隐私弹窗文案验证失败: {result['reason']} | 问题: {result.get('issues', [])}"

            # 点同意，继续流程
            page.tap(*BTN_AGREE)
            page.wait_seconds(1)
        else:
            allure.attach("隐私弹窗未出现，跳过", name="隐私弹窗", attachment_type=allure.attachment_type.TEXT)

    # ── Step 3: 处理通知权限弹窗 ──
    with allure.step("处理通知权限弹窗"):
        handle_notification_permission(page)

    # ── Step 4: 引导页验证 ──
    with allure.step("验证引导页文案"):
        page.wait_seconds(2)
        if page.is_visible(*BTN_NEXT, timeout=5):
            guide_copy = get_copy_for_lang("splash", lang_code)
            # 只取引导页相关 key（guide_ 开头 + btn_next）
            guide_keys = {k: v for k, v in guide_copy.items()
                         if k.startswith("guide") or k.startswith("onboard") or k == "btn_next"}

            screenshot = android_driver.get_screenshot_as_base64()
            allure.attach(
                android_driver.get_screenshot_as_png(),
                name=f"引导页_{lang_name}",
                attachment_type=allure.attachment_type.PNG
            )

            result = assert_copy_by_vision(
                screenshot_base64=screenshot,
                lang_display_name=lang_name,
                expected_copy=guide_keys,
                page_desc="引导页"
            )
            allure.attach(
                str(result),
                name=f"断言结果_{lang_name}_引导页",
                attachment_type=allure.attachment_type.TEXT
            )
            assert result["result"] != "fail", \
                f"[{lang_name}] 引导页文案验证失败: {result['reason']} | 问题: {result.get('issues', [])}"

            # 点下一步
            page.tap(*BTN_NEXT)
            page.wait_seconds(1)
        else:
            allure.attach("引导页未出现，跳过", name="引导页", attachment_type=allure.attachment_type.TEXT)

    # ── Step 5: 国家选择页验证 ──
    with allure.step("验证国家选择页文案"):
        page.wait_seconds(2)
        if page.is_visible(*BTN_SURE, timeout=5):
            country_copy = get_copy_for_lang("splash", lang_code)
            # 取国家选择页相关 key（country_ 开头 + btn_sure + 页面标题）
            country_keys = {k: v for k, v in country_copy.items()
                           if k.startswith("country") or k.startswith("select_")
                           or k in ("btn_sure", "btn_confirm")}

            screenshot = android_driver.get_screenshot_as_base64()
            allure.attach(
                android_driver.get_screenshot_as_png(),
                name=f"国家选择页_{lang_name}",
                attachment_type=allure.attachment_type.PNG
            )

            result = assert_copy_by_vision(
                screenshot_base64=screenshot,
                lang_display_name=lang_name,
                expected_copy=country_keys,
                page_desc="国家地区选择页"
            )
            allure.attach(
                str(result),
                name=f"断言结果_{lang_name}_国家选择页",
                attachment_type=allure.attachment_type.TEXT
            )
            assert result["result"] != "fail", \
                f"[{lang_name}] 国家选择页文案验证失败: {result['reason']} | 问题: {result.get('issues', [])}"
        else:
            allure.attach("国家选择页未出现，跳过", name="国家选择页", attachment_type=allure.attachment_type.TEXT)
