#!/usr/bin/env python3
"""
Liene APP 自动化 Runner
功能：轮询 Supabase run_tasks 表，发现新任务自动触发 pytest，结果写回 run_results
使用：python3 runner.py
"""

import os
import time
import subprocess
from datetime import datetime, timezone
from supabase import create_client, Client

SUPABASE_URL  = os.environ.get("SUPABASE_URL", "https://pgpnyrglrromqqjnvaix.supabase.co")
SUPABASE_KEY  = os.environ.get("SUPABASE_KEY", "")
FRAMEWORK_DIR = os.path.expanduser("~/liene-app-automation")
POLL_INTERVAL = 5

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 模块 → pytest 命令映射
MODULE_CMD = {
    "smoke":              ["-m", "smoke"],
    "regression":         ["-m", "regression"],
    "splash":             ["-m", "splash"],
    "splash_i18n":        ["tests/smoke/test_splash_i18n.py"],
    "login":              ["-m", "login"],
    "homepage_perilla":   ["-m", "homepage_perilla"],
    "homepage_kiwi":      ["-m", "homepage_kiwi"],
    "homepage_cumin":     ["-m", "homepage_cumin"],
    "homepage_laurel":    ["-m", "homepage_laurel"],
    "homepage_fennel":    ["-m", "homepage_fennel"],
}


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def update_task_status(task_id: str, status: str):
    data = {"status": status}
    if status == "running":
        data["started_at"] = datetime.now(timezone.utc).isoformat()
    if status in ("done", "failed"):
        data["finished_at"] = datetime.now(timezone.utc).isoformat()
    supabase.table("run_tasks").update(data).eq("id", task_id).execute()


def write_results(task_id: str, results: list):
    if not results:
        return
    rows = [{
        "task_id":     task_id,
        "case_name":   r.get("case_name"),
        "result":      r.get("result"),
        "reason":      r.get("reason"),
        "duration_ms": r.get("duration_ms"),
    } for r in results]
    supabase.table("run_results").insert(rows).execute()


def parse_pytest_output(output: str) -> list:
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


def build_pytest_cmd(task: dict) -> list:
    """根据任务构建 pytest 命令"""
    task_type = task.get("task_type", "smoke")
    module    = task.get("module", "")      # 新增模块字段
    platform  = task.get("platform", "android")

    # 优先用 module 字段，没有则用 task_type
    key = module if module and module in MODULE_CMD else task_type
    args = MODULE_CMD.get(key, ["-m", "smoke"])

    cmd = ["python3", "-m", "pytest"] + args + [
        "-v",
        f"--alluredir={FRAMEWORK_DIR}/reports/allure-results",
    ]
    return cmd


def run_pytest(task: dict) -> tuple:
    cmd = build_pytest_cmd(task)
    env = os.environ.copy()
    env["AUTOMATION_PLATFORM"] = task.get("platform", "android")

    log(f"执行：{' '.join(cmd)}")

    try:
        proc = subprocess.run(
            cmd, cwd=FRAMEWORK_DIR,
            capture_output=True, text=True,
            timeout=1800, env=env,
        )
        results = parse_pytest_output(proc.stdout + proc.stderr)
        return proc.returncode == 0, results
    except subprocess.TimeoutExpired:
        return False, [{"case_name": "timeout", "result": "error", "reason": "执行超时"}]
    except Exception as e:
        return False, [{"case_name": "exception", "result": "error", "reason": str(e)}]


def poll():
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
    log(f"新任务：{task_id} 类型={task['task_type']} 模块={task.get('module','-')} 平台={task['platform']}")

    update_task_status(task_id, "running")
    success, results = run_pytest(task)
    write_results(task_id, results)
    update_task_status(task_id, "done" if success else "failed")

    pass_count = sum(1 for r in results if r["result"] == "pass")
    fail_count = sum(1 for r in results if r["result"] in ("fail", "error"))
    log(f"完成：{'done' if success else 'failed'} 通过={pass_count} 失败={fail_count}")


def main():
    log("Runner 启动，监听任务队列...")
    if not SUPABASE_KEY:
        print("\n⚠️  请先设置：export SUPABASE_KEY='your_service_role_key'\n")
        return
    while True:
        try:
            poll()
        except Exception as e:
            log(f"轮询异常：{e}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
