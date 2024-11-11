import asyncio
import json
import random
import ssl
import uuid
import time
from fastapi import FastAPI, WebSocket, APIRouter, BackgroundTasks, UploadFile, File, HTTPException
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from loguru import logger
from typing import Dict, List, Optional
from websockets_proxy import Proxy, proxy_connect
from fake_useragent import UserAgent
import re

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

user_agent = UserAgent()
nstProxyAppId = "F680F8381EB0D52B"
all_clients: Dict[str, asyncio.Task] = {}

# 定义用户请求的数据模型
class ClientData(BaseModel):
    user_id: str
    proxy_url: Optional[str] = None

# 验证代理 URL 格式
def validate_proxy_url(proxy_url: str) -> bool:
    pattern = r"^(http|https|socks5)://[^:@\s]+:[^:@\s]+@[\d\.]+:\d+$"
    return bool(re.match(pattern, proxy_url))

# 验证用户 ID 格式
def validate_user_id(user_id: str) -> bool:
    pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
    return bool(re.match(pattern, user_id))

# 添加 nstproxy appid 到代理用户名
def add_nstproxy_appid(proxy: str) -> str:
    if "nstproxy." in proxy:
        pattern = r"^(?:[^:]+)://([^:]+):[^@]+@"
        match = re.match(pattern, proxy)
        if match:
            username = match.group(1)
            if "appId" not in username:
                new_username = f"{username}-appid_{nstProxyAppId}"
                proxy = proxy.replace(username, new_username)
    return proxy

# 建立 WebSocket 连接
async def connect_to_wss(socks5_proxy, user_id):
    device_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, socks5_proxy))
    custom_headers = {"User-Agent": user_agent.random}
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    uri_list = ["wss://proxy.wynd.network:4444/", "wss://proxy.wynd.network:4650/"]
    uri = random.choice(uri_list)
    proxy = Proxy.from_url(socks5_proxy)
    server_hostname = "proxy.wynd.network"

    try:
        async with proxy_connect(uri, proxy=proxy, ssl=ssl_context, server_hostname=server_hostname,
                                 extra_headers=custom_headers) as websocket:
            async def send_ping():
                while True:
                    await websocket.send(json.dumps({"id": str(uuid.uuid4()), "version": "1.0.0", "action": "PING"}))
                    await asyncio.sleep(60)

            asyncio.create_task(send_ping())

            while True:
                response = await websocket.recv()
                message = json.loads(response)
                if message.get("action") == "AUTH":
                    auth_response = {
                        "id": message["id"],
                        "origin_action": "AUTH",
                        "result": {
                            "browser_id": device_id,
                            "user_id": user_id,
                            "user_agent": custom_headers['User-Agent'],
                            "timestamp": int(time.time()),
                            "device_type": "desktop",
                            "version": "4.28.1"
                        }
                    }
                    await websocket.send(json.dumps(auth_response))
                elif message.get("action") == "PONG":
                    await websocket.send(json.dumps({"id": message["id"], "origin_action": "PONG"}))

    except Exception as e:
        logger.error(f"Error in WebSocket connection: {e}")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/client/")
async def add_client(client_data: ClientData, background_tasks: BackgroundTasks):
    user_id = client_data.user_id
    proxy_url = client_data.proxy_url

    if not validate_user_id(user_id):
        return {"error": "Invalid user ID format"}
    if proxy_url and not validate_proxy_url(proxy_url):
        return {"error": "Invalid proxy URL format"}

    client_id = str(uuid.uuid4())
    proxy = add_nstproxy_appid(proxy_url) if proxy_url else proxy_url
    task = asyncio.create_task(connect_to_wss(proxy, user_id))
    all_clients[client_id] = task
    background_tasks.add_task(task)
    return {"client_id": client_id, "message": "Client added successfully"}

@app.delete("/client/{client_id}")
async def delete_client(client_id: str):
    if client_id in all_clients:
        task = all_clients.pop(client_id)
        task.cancel()
        return {"message": "Client removed successfully"}
    return {"error": "Client not found"}

@app.delete("/client/")
async def delete_all_clients():
    for client_id, task in list(all_clients.items()):
        task.cancel()
        all_clients.pop(client_id)
    return {"message": "All clients removed successfully"}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    lines = content.decode().splitlines()

    added_clients = []
    for line in lines:
        if "==" in line:
            user_id, proxy_url = line.split("==")
            proxy_url = proxy_url.strip()
        else:
            user_id, proxy_url = line.strip(), None

        if not validate_user_id(user_id):
            continue
        if proxy_url and not validate_proxy_url(proxy_url):
            continue

        client_id = str(uuid.uuid4())
        proxy = add_nstproxy_appid(proxy_url) if proxy_url else None
        task = asyncio.create_task(connect_to_wss(proxy, user_id))
        all_clients[client_id] = task
        added_clients.append(client_id)

    return {"message": "File processed", "added_clients": added_clients}

@app.get("/client/")
async def list_clients():
    client_list = [{"client_id": client_id, "status": task.done()} for client_id, task in all_clients.items()]
    return {"clients": client_list}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
