from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from app.utils import add_nstproxy_appid, validate_user_id, connect_to_wss
import asyncio
import json

app = FastAPI()

clients = {}

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("app/templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/client/")
async def add_client(user_id: str, proxy_url: str):
    if not validate_user_id(user_id):
        raise HTTPException(status_code=400, detail="Invalid User ID format.")
    proxy_url = add_nstproxy_appid(proxy_url)
    clients[user_id] = {"proxy_url": proxy_url, "status": "pending"}
    asyncio.create_task(connect_to_wss(proxy_url, user_id))
    return {"status": "success", "user_id": user_id}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    lines = content.decode("utf-8").splitlines()
    for line in lines:
        if "--" in line:
            user_id, proxy = line.split("--", 1)
            await add_client(user_id.strip(), proxy.strip())
    return {"status": "file processed"}

@app.post("/clear/")
async def clear_clients():
    clients.clear()
    return {"status": "all clients cleared"}

@app.get("/clients/")
async def list_clients():
    return clients
