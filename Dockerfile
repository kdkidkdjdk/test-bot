# 使用官方 Python 镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 将当前目录的内容复制到容器中
COPY . .

# 安装所需的 Python 依赖
RUN pip install -r requirements.txt

# 暴露所需端口
EXPOSE 8000

# 定义启动命令
CMD ["python", "getgrassDesktopBot.py"]
