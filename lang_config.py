"""
17语言配置
lang_code: Supabase copy_texts 表字段名
android_locale: adb 切换系统语言用的 locale
display_name: 日志显示名
"""

LANGUAGES = [
    {"lang_code": "en",    "android_locale": "en-US",  "display_name": "English"},
    {"lang_code": "zh",    "android_locale": "zh-CN",  "display_name": "简体中文"},
    {"lang_code": "de",    "android_locale": "de-DE",  "display_name": "Deutsch"},
    {"lang_code": "es",    "android_locale": "es-ES",  "display_name": "Español"},
    {"lang_code": "fr",    "android_locale": "fr-FR",  "display_name": "Français"},
    {"lang_code": "it",    "android_locale": "it-IT",  "display_name": "Italiano"},
    {"lang_code": "ja",    "android_locale": "ja-JP",  "display_name": "日本語"},
    {"lang_code": "ru",    "android_locale": "ru-RU",  "display_name": "Русский"},
    {"lang_code": "ko",    "android_locale": "ko-KR",  "display_name": "한국어"},
    {"lang_code": "zh_TW", "android_locale": "zh-TW",  "display_name": "繁體中文"},
    {"lang_code": "pl",    "android_locale": "pl-PL",  "display_name": "Polski"},
    {"lang_code": "da",    "android_locale": "da-DK",  "display_name": "Dansk"},
    {"lang_code": "fi",    "android_locale": "fi-FI",  "display_name": "Suomi"},
    {"lang_code": "nl",    "android_locale": "nl-NL",  "display_name": "Nederlands"},
    {"lang_code": "cs",    "android_locale": "cs-CZ",  "display_name": "Čeština"},
    {"lang_code": "nb",    "android_locale": "nb-NO",  "display_name": "Norsk"},
    {"lang_code": "sv",    "android_locale": "sv-SE",  "display_name": "Svenska"},
]

# 按 lang_code 快速查找
LANG_MAP = {l["lang_code"]: l for l in LANGUAGES}
