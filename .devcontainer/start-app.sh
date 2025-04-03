#!/bin/bash

# 设置颜色输出
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

# 定义一个函数以启动后端服务
start_backend() {
    echo -e "${YELLOW}启动后端服务...${NC}"
    cd /workspace/backend
    python init_db.py
    python -m flask run --host=0.0.0.0 --port=5000 &
    echo -e "${GREEN}后端服务已启动在: http://localhost:5000${NC}"
}

# 定义一个函数以启动前端服务
start_frontend() {
    echo -e "${YELLOW}启动前端服务...${NC}"
    cd /workspace/frontend
    npm install
    npm run dev &
    echo -e "${GREEN}前端服务已启动在: http://localhost:3000${NC}"
}

echo -e "${YELLOW}正在启动WebArt应用...${NC}"

# 启动所有服务
start_backend
start_frontend

echo -e "${GREEN}所有服务已启动!${NC}"
echo -e "${YELLOW}前端: ${NC}http://localhost:3000"
echo -e "${YELLOW}后端API: ${NC}http://localhost:5000/api"
echo -e "${YELLOW}按Ctrl+C停止所有服务${NC}"

# 保持脚本运行
wait 