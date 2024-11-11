# 使用 Python 3.9 作为基础镜像
FROM python:3.9

# 设置工作目录
WORKDIR /app

# 复制项目的所有文件到容器中
COPY . .

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露应用运行的端口
EXPOSE 8000

# 运行 FastAPI 应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
