"""
DeepSeek Vision 多语言文案视觉断言
"""
import os
import json
import requests
import base64

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"


def assert_copy_by_vision(
    screenshot_base64: str,
    lang_display_name: str,
    expected_copy: dict,
    page_desc: str = "",
) -> dict:
    """
    用 DeepSeek Vision 验证截图中的多语言文案
    
    Args:
        screenshot_base64: 截图 base64
        lang_display_name: 语言名称（如 "Deutsch"）
        expected_copy: { key: expected_text } 预期文案字典
        page_desc: 页面描述（如 "隐私协议弹窗"）
    
    Returns:
        {
            "result": "pass" | "fail",
            "reason": "...",
            "issues": ["具体问题1", "具体问题2"]
        }
    """
    # 格式化预期文案
    expected_lines = []
    for key, text in expected_copy.items():
        if text and text.strip():
            expected_lines.append(f"- {key}: 「{text}」")

    if not expected_lines:
        return {"result": "skip", "reason": "该语言无预期文案数据", "issues": []}

    expected_str = "\n".join(expected_lines)

    prompt = f"""你是一个移动端 APP 多语言文案测试专家。

请仔细查看这张截图，这是 Liene Photo APP 在 **{lang_display_name}** 语言下的 **{page_desc}** 页面截图。

【预期文案】
{expected_str}

【验证要求】
1. 截图中是否能看到上述预期文案？
2. 文案是否显示完整，没有被截断（...）或溢出边界？
3. 是否有乱码或显示为 key 名称（如 btn_next）而非实际文案？
4. 文案语言是否与预期语言（{lang_display_name}）一致？

【注意】
- 截图中可能只显示部分预期文案（如弹窗只显示部分内容），只验证截图中可见的部分
- 如果文案在截图中不可见（被遮挡或在屏幕外），不算失败
- 重点关注：截断、乱码、语言错误、文案缺失

请只返回 JSON，不要其他文字：
{{"result": "pass/fail/skip", "reason": "一句话总结", "issues": ["具体问题1（如有）"]}}"""

    payload = {
        "model": "deepseek-vl2",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{screenshot_base64}"}
                    },
                    {"type": "text", "text": prompt}
                ]
            }
        ],
        "max_tokens": 512,
        "response_format": {"type": "json_object"}
    }

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        return {"result": "error", "reason": f"DeepSeek API 调用失败: {e}", "issues": []}
