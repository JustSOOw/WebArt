# 使用官方 Python 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建静态目录和上传文件夹
RUN mkdir -p /app/static/uploads/images \
    /app/static/uploads/audio \
    /app/static/uploads/video \
    /app/static/uploads/documents \
    && chmod -R 777 /app/static/uploads

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 5000

# 创建启动脚本
RUN echo '#!/bin/sh\n\
python init_db.py\n\
gunicorn --bind 0.0.0.0:5000 "app:create_app()"\n\
' > /app/start.sh && chmod +x /app/start.sh

# 启动命令
CMD ["/app/start.sh"]