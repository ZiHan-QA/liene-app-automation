#!/usr/bin/env python3
"""
Liene APP 自动化 Runner
功能：轮询 Supabase run_tasks 表，发现新任务自动触发 pytest，结果写回 run_results
使用：python3 runner.py
"""

import os
import time
import subprocess
import json
import re
from datetime import datetime, timezone
from supabase import create_client, Client

# ── 配置 ──────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://pgpnyrglrromqqjnvaix.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")  # 填写 service_role key
FRAMEWORK_DIR = os.path.expanduser("~/liene-app-automation")
POLL_INTERVAL = 5  # 秒

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


def update_task_status(task_id: str, status: str, extra: dict = None):
    data = {"status": status}
    if status == "running":
        data["started_at"] = datetime.now(timezone.utc).isoformat()
    if status in ("done", "failed"):
        data["finished_at"] = datetime.now(timezone.utc).isoformat()
    if extra:
        data.update(extra)
    supabase.table("run_tasks").update(data).eq("id", task_id).execute()


def write_results(task_id: str, results: list):
    if not results:
        return
    rows = [
        {
            "task_id": task_id,
            "case_name": r.get("case_name"),
            "result": r.get("result"),
            "reason": r.get("reason"),
            "duration_ms": r.get("duration_ms"),
        }
        for r in results
    ]
    supabase.table("run_results").insert(rows).execute()


def parse_pytest_output(output: str) -> list:
    """从 pytest -v 输出中解析用例结果"""
    results = []
    for line in output.splitlines():
        if " PASSED" in line:
            name = line.split("::")[1].split(" ")[0] if "::" in line else line
            results.append({"case_name": name.strip(), "result": "pass", "reason": ""})
        elif " FAILED" in line:
            name = line.split("::")[1].split(" ")[0] if "::" in line else line
            results.append({"case_name": name.strip(), "result": "fail", "reason": "见 Allure 报告"})
        elif " ERROR" in line:
            name = line.split("::")[1].split(" ")[0] if "::" in line else line
            results.append({"case_name": name.strip(), "result": "error", "reason": "执行出错"})
    return results


def run_pytest(task: dict) -> tuple[bool, list]:
    """根据任务类型执行 pytest，返回 (是否成功, 结果列表)"""
    task_type = task.get("task_type", "smoke")
    platform = task.get("platform", "android")

    # 构建 pytest 命令
    cmd = [
        "python3", "-m", "pytest",
        f"-m", task_type,
        "-v",
        f"--alluredir={FRAMEWORK_DIR}/reports/allure-results",
    ]

    # 平台参数通过环境变量传入
    env = os.environ.copy()
    env["AUTOMATION_PLATFORM"] = platform

    log(f"执行命令：{' '.join(cmd)}")
    log(f"平台：{platform}，类型：{task_type}")

    try:
        proc = subprocess.run(
            cmd,
            cwd=FRAMEWORK_DIR,
            capture_output=True,
            text=True,
            timeout=600,  # 10分钟超时
            env=env,
        )
        output = proc.stdout + proc.stderr
        log(f"pytest 退出码：{proc.returncode}")
        results = parse_pytest_output(output)
        success = proc.returncode == 0
        return success, results
    except subprocess.TimeoutExpired:
        log("pytest 超时（10分钟）")
        return False, [{"case_name": "timeout", "result": "error", "reason": "执行超时"}]
    except Exception as e:
        log(f"执行异常：{e}")
        return False, [{"case_name": "exception", "result": "error", "reason": str(e)}]


def poll():
    """轮询一次任务队列"""
    resp = (
        supabase.table("run_tasks")
        .select("*")
        .eq("status", "queued")
        .order("created_at")
        .limit(1)
        .execute()
    )
    if not resp.data:
        return

    task = resp.data[0]
    task_id = task["id"]
    log(f"发现新任务：{task_id}  类型={task['task_type']}  平台={task['platform']}")

    # 标记为运行中
    update_task_status(task_id, "running")

    # 执行 pytest
    success, results = run_pytest(task)

    # 写回结果
    write_results(task_id, results)
    final_status = "done" if success else "failed"
    update_task_status(task_id, final_status)

    pass_count = sum(1 for r in results if r["result"] == "pass")
    fail_count = sum(1 for r in results if r["result"] in ("fail", "error"))
    log(f"任务完成：{final_status}  通过={pass_count}  失败={fail_count}")


def main():
    log("Runner 启动，开始监听任务队列...")
    log(f"框架目录：{FRAMEWORK_DIR}")
    log(f"轮询间隔：{POLL_INTERVAL}s")

    if not SUPABASE_KEY:
        print("\n⚠️  请先设置环境变量：")
        print("  export SUPABASE_KEY='your_service_role_key'")
        print("  然后重新运行：python3 runner.py\n")
        return

    while True:
        try:
            poll()
        except Exception as e:
            log(f"轮询异常：{e}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
