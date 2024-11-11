from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uuid

app = FastAPI()

# 临时存储客户端数据
clients = {}

# 静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")

class ClientData(BaseModel):
    user_id: str
    proxy_url: str = None

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("templates/index.html") as f:
        return f.read()

@app.post("/client/")
async def add_client(data: ClientData):
    client_id = str(uuid.uuid4())
    clients[client_id] = {"user_id": data.user_id, "proxy": data.proxy_url, "status": True}
    return {"message": "Client added successfully"}

@app.get("/clients/")
async def get_clients():
    return [{"user_id": client["user_id"], "proxy": client["proxy"], "status": client["status"]} for client in clients.values()]

@app.post("/clear/")
async def clear_clients():
    clients.clear()
    return {"message": "All clients cleared"}

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

@app.delete("/client/{user_id}")
async def delete_client(user_id: str):
    for client_id, client in list(clients.items()):
        if client["user_id"] == user_id:
            del clients[client_id]
            return {"message": "Client deleted successfully"}
    raise HTTPException(status_code=404, detail="Client not found")
