# 使用官方 Python 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libffi-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn && \
    rm -rf /root/.cache/pip

# 创建必要的目录结构
RUN mkdir -p /app/static/uploads/images \
    /app/static/uploads/audio \
    /app/static/uploads/video_sources \
    /app/static/uploads/documents \
    /app/data \
    && chmod -R 777 /app/static/uploads /app/data

# 复制应用代码
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app \
    FLASK_ENV=production \
    FLASK_DEBUG=0

# 暴露端口
EXPOSE 5000

# 创建启动脚本
RUN echo '#!/bin/sh\n\
    python init_db.py\n\
    gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 "app:create_app()"\n\
    ' > /app/start.sh && chmod +x /app/start.sh

# 启动命令
CMD ["/app/start.sh"]