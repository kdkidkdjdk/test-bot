# 使用 Python 3.9 作为基础镜像
FROM python:3.9

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY ./app /app

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露 FastAPI 端口
EXPOSE 8000

# 运行 FastAPI 服务器
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
