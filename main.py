from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
import os

app = FastAPI()

# 模拟账户数据
accounts = [
    {"id": 1, "user_id": "d74baedf...", "proxy": "socks5://...", "status": "已连接"},
    {"id": 2, "user_id": "ea190434...", "proxy": "socks5://...", "status": "已连接"},
    # 添加其他账户数据
]

@app.get("/")
async def main():
    with open("templates/index.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/api/accounts")
async def get_accounts():
    return {"accounts": accounts}

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    file_location = f"/app/{file.filename}"
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())
    return {"info": f"文件 '{file.filename}' 已上传至 {file_location}"}
