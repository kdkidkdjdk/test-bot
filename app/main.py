from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict
import uuid
import json

app = FastAPI()

# 用于存储客户端信息
clients: Dict[str, Dict] = {}

# 定义客户端数据模型
class ClientData(BaseModel):
    user_id: str
    proxy_url: Optional[str] = None

# 首页路由，返回 HTML 页面
@app.get("/")
async def get_index():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

# 添加客户端的路由
@app.post("/client/")
async def add_client(data: ClientData):
    # 打印接收到的数据
    print(f"Received data: user_id={data.user_id}, proxy_url={data.proxy_url}")
    
    # 模拟处理逻辑，如限制特定的 user_id
    if data.user_id in ["restricted-id"]:
        raise HTTPException(status_code=400, detail="Restricted user ID")

    # 生成客户端 ID，并添加到 clients 字典
    client_id = str(uuid.uuid4())
    clients[client_id] = {"user_id": data.user_id, "proxy": data.proxy_url, "status": "connected"}
    
    print(f"Client added with ID: {client_id}")  # 记录添加成功的日志
    return {"message": "Client added successfully", "client_id": client_id}

# 获取所有客户端信息的路由
@app.get("/clients/")
async def get_clients():
    # 返回所有客户端信息
    return [{"client_id": client_id, "user_id": data["user_id"], "proxy": data["proxy"], "status": data["status"]} for client_id, data in clients.items()]

# 清空所有客户端的路由
@app.post("/clear/")
async def clear_clients():
    clients.clear()  # 清空所有客户端
    print("All clients have been cleared.")  # 记录清空操作
    return {"message": "All clients cleared"}

# 删除指定客户端的路由
@app.delete("/client/{client_id}")
async def delete_client(client_id: str):
    # 检查客户端是否存在并删除
    if client_id in clients:
        del clients[client_id]
        print(f"Client with ID {client_id} deleted.")  # 记录删除操作
        return {"message": "Client deleted successfully"}
    raise HTTPException(status_code=404, detail="Client not found")

# 文件上传并批量添加客户端的路由
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # 读取文件内容并逐行解析
    content = await file.read()
    lines = content.decode("utf-8").splitlines()
    added_clients = []
    for line in lines:
        # 解析 user_id 和 proxy_url
        parts = line.split("==")
        user_id = parts[0].strip()
        proxy_url = parts[1].strip() if len(parts) > 1 else None
        client_id = str(uuid.uuid4())
        clients[client_id] = {"user_id": user_id, "proxy": proxy_url, "status": "connected"}
        added_clients.append(client_id)
        print(f"Added client from file: user_id={user_id}, proxy_url={proxy_url}")  # 打印文件处理日志

    return {"message": "File processed successfully", "added_clients": added_clients}

# 获取指定客户端日志（示例）
@app.get("/client/{client_id}/logs")
async def get_logs(client_id: str):
    if client_id not in clients:
        raise HTTPException(status_code=404, detail="Client not found")
    # 返回示例日志
    return {"logs": ["Log entry 1", "Log entry 2", "Log entry 3"]}
