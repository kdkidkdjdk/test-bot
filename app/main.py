# main.py - FastAPI backend with WebSocket connections

import asyncio
from typing import Optional, Dict, List
from pydantic import BaseModel
from fastapi import FastAPI, WebSocket, BackgroundTasks, UploadFile, File
from fastapi.responses import HTMLResponse
from starlette.requests import Request
import uuid
import re

app = FastAPI()

clients = {}

class ClientData(BaseModel):
    user_id: str
    proxy_url: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/client/")
async def add_client(data: ClientData, background_tasks: BackgroundTasks):
    client_id = str(uuid.uuid4())
    clients[client_id] = {"user_id": data.user_id, "proxy": data.proxy_url, "status": True}
    return {"message": "Client added successfully", "client_id": client_id}

@app.get("/client/")
async def list_clients():
    return {"clients": [{"client_id": k, **v} for k, v in clients.items()]}

@app.delete("/client/{client_id}")
async def delete_client(client_id: str):
    if client_id in clients:
        del clients[client_id]
        return {"message": "Client deleted successfully"}
    return {"error": "Client not found"}

@app.delete("/client/")
async def delete_all_clients():
    clients.clear()
    return {"message": "All clients deleted successfully"}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    lines = content.decode("utf-8").splitlines()
    for line in lines:
        parts = line.split("==")
        user_id = parts[0].strip()
        proxy_url = parts[1].strip() if len(parts) > 1 else None
        client_id = str(uuid.uuid4())
        clients[client_id] = {"user_id": user_id, "proxy": proxy_url, "status": True}
    return {"message": "File processed successfully"}

@app.get("/client/{client_id}/logs")
async def get_logs(client_id: str):
    # Placeholder for actual logs; currently returns dummy data
    return {"logs": ["Log entry 1", "Log entry 2", "Log entry 3"]}
