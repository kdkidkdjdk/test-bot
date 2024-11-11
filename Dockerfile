# 使用Python 3.9基础镜像
FROM python:3.9

# 设置工作目录
WORKDIR /app

# 复制项目文件到容器
COPY . .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8000

# 启动FastAPI应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
