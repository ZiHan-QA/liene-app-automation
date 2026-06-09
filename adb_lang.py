"""
通过 adb 切换 Android 系统语言并重启 APP
"""
import subprocess
import time


APP_PACKAGE = "com.hannto.flutterModule.liene_photo"
APP_ACTIVITY = ".MainActivity"


def run_adb(cmd: str, timeout: int = 15) -> str:
    result = subprocess.run(
        f"adb {cmd}", shell=True,
        capture_output=True, text=True, timeout=timeout
    )
    return result.stdout.strip()


def set_language(android_locale: str):
    """
    切换系统语言
    android_locale: 如 "en-US", "zh-CN", "ja-JP"
    """
    lang, region = android_locale.split("-") if "-" in android_locale else (android_locale, "")
    # 通过 am 广播切换语言（免 root，需 API 29+）
    run_adb(f'shell am broadcast -a com.android.internal.intent.action.LOCALE_CHANGED')
    # 使用 LocaleOverlayHelper 或直接设置（MIUI/原生）
    run_adb(f'shell settings put system system_locales {android_locale}')
    run_adb(f'shell am broadcast -a android.intent.action.LOCALE_CHANGED')
    time.sleep(1)


def force_stop_app():
    run_adb(f"shell am force-stop {APP_PACKAGE}")
    time.sleep(1)


def clear_app_data():
    """清除 APP 数据，模拟首次安装"""
    run_adb(f"shell pm clear {APP_PACKAGE}")
    time.sleep(2)


def launch_app():
    run_adb(f"shell am start -n {APP_PACKAGE}/{APP_ACTIVITY}")
    time.sleep(4)  # 等待启动完成


def restart_app_with_lang(android_locale: str, clear_data: bool = False):
    """
    切换语言后重启 APP
    clear_data=True 时清除数据（模拟首次安装，会出现引导页）
    """
    set_language(android_locale)
    force_stop_app()
    if clear_data:
        clear_app_data()
    launch_app()
