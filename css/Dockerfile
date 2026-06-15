# 使用 Python 官方镜像作为基础
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖清单
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制所有代码文件
COPY . .

# 暴露端口
EXPOSE 3000

# 启动命令
CMD ["python", "server.py"]
