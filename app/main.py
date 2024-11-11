from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import asyncio
from utils import load_accounts, connect_to_wss

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 读取并展示主页
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    accounts = load_accounts()
    return templates.TemplateResponse("index.html", {"request": request, "accounts": accounts})

# 启动 WebSocket 连接
@app.get("/start")
async def start_connections():
    asyncio.create_task(connect_to_wss())
    return {"status": "WebSocket connections started"}
