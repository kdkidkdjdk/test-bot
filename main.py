from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
import asyncio
import os
from getgrassDesktopBot import load_proxies, connect_to_wss

app = FastAPI()

# 模拟账户数据
accounts = [{"id": i + 1, "user_id": f"user_{i}", "proxy": "socks5://...", "status": "未连接"} for i in range(5)]
connections = {}  # 用于存储用户连接任务

@app.get("/")
async def main():
    with open("templates/index.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/api/accounts")
async def get_accounts():
    return {"accounts": accounts}

@app.post("/api/start_connection")
async def start_connection(background_tasks: BackgroundTasks):
    proxies = load_proxies()
    tasks = [asyncio.create_task(connect_to_wss(proxy, user_id)) for user_id, proxy in proxies]
    connections.update({user_id: task for user_id, task in zip([p[0] for p in proxies], tasks)})
    background_tasks.add_task(asyncio.gather, *tasks)
    for account in accounts:
        account["status"] = "已连接"
    return {"status": "连接已启动"}

@app.post("/api/stop_connection")
async def stop_connection():
    for user_id, task in connections.items():
        task.cancel()
    connections.clear()
    for account in accounts:
        account["status"] = "已断开"}
    return {"status": "连接已停止"}
