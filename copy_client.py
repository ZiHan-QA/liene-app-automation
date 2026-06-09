"""
从 Supabase copy_texts 表拉取文案
运行时动态读取，不依赖硬编码 key
"""
import os
import requests
from functools import lru_cache

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://pgpnyrglrromqqjnvaix.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBncG55cmdscnJvbXFxam52YWl4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA2MjY2OTgsImV4cCI6MjA5NjIwMjY5OH0.TmkrxS2mY_95aBC2UL2BARLU7gqNb_gSpHP6ynofDsE")


@lru_cache(maxsize=32)
def get_page_copy(page: str) -> dict:
    """
    拉取指定页面所有文案
    返回：{ key: { lang_code: text, ... }, ... }
    """
    url = f"{SUPABASE_URL}/rest/v1/copy_texts"
    params = {"page": f"eq.{page}", "select": "*"}
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    rows = resp.json()

    result = {}
    for row in rows:
        key = row["key"]
        result[key] = {k: v for k, v in row.items()
                       if k not in ("id", "page", "key", "remark", "updated_by", "updated_at")}
    return result


def get_copy_for_lang(page: str, lang_code: str) -> dict:
    """
    获取指定页面、指定语言的所有文案
    返回：{ key: text, ... }
    """
    all_copy = get_page_copy(page)
    return {key: texts.get(lang_code, "") for key, texts in all_copy.items()}


def format_expected_copy(copy_dict: dict) -> str:
    """
    把文案字典格式化成给 DeepSeek 的预期文案描述
    过滤掉空值
    """
    lines = []
    for key, text in copy_dict.items():
        if text and text.strip():
            lines.append(f"- {key}: 「{text}」")
    return "\n".join(lines)
