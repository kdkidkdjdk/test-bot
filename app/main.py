import asyncio
import json
import random
import ssl
import uuid
import time
from fastapi import FastAPI, WebSocket, APIRouter, BackgroundTasks, UploadFile, File, HTTPException
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from loguru import logger
from typing import Dict, List, Optional
from websockets_proxy import Proxy, proxy_connect
from fake_useragent import UserAgent
import re

from app.utils import add_nstproxy_appid, validate_user_id, validate_proxy_url

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

user_agent = UserAgent()
nstProxyAppId = "F680F8381EB0D52B"
all_clients: Dict[str, asyncio.Task] = {}

async def connect_to_wss(socks5_proxy, user_id):
    device_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, socks5_proxy))
    custom_headers = {"User-Agent": user_agent.random}
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    uriList = ["wss://proxy.wynd.network:4444/", "wss://proxy.wynd.network:4650/"]
    uri = random.choice(uriList)
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
async def add_client(user_id: str, proxy_url: str, background_tasks: BackgroundTasks):
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
