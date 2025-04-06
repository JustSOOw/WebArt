#!/bin/bash
###
 # @Author: JustSOOw wang813104@outlook.com
 # @Date: 2025-04-03 21:15:31
 # @LastEditors: JustSOOw wang813104@outlook.com
 # @LastEditTime: 2025-04-05 19:38:22
 # @FilePath: \WebArt\.devcontainer\start-app.sh
 # @Description: 
 # 
 # Copyright (c) 2025 by Furdow, All Rights Reserved. 
### 

# 设置颜色输出
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m" # Added Red color for errors
NC="\033[0m" # No Color

BACKEND_PID=""
FRONTEND_PID=""

# 清理函数，用于停止后台进程
cleanup() {
    echo -e "${YELLOW}收到停止信号，正在清理后台进程...${NC}"
    # Kill backend process if PID exists
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID > /dev/null 2>&1
        echo -e "${GREEN}已停止后端进程 (PID: $BACKEND_PID)${NC}"
    fi
    # Kill frontend process if PID exists
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID > /dev/null 2>&1
        echo -e "${GREEN}已停止前端进程 (PID: $FRONTEND_PID)${NC}"
    fi
    exit 0
}

# 捕获 SIGINT (Ctrl+C) 和 SIGTERM 信号，并执行 cleanup 函数
trap cleanup SIGINT SIGTERM

# 定义一个函数以启动后端服务
start_backend() {
    echo -e "${YELLOW}启动后端服务...${NC}"
    cd /workspace/backend || exit 1 # Exit if cd fails
    if [ -f init_db.py ]; then
        python init_db.py
    else
        echo -e "${YELLOW}警告: init_db.py 未找到，跳过数据库初始化。${NC}"
    fi
    python -m flask run --host=0.0.0.0 --port=5000 &
    BACKEND_PID=$! # 保存后端进程的PID
    echo -e "${GREEN}后端服务已启动 (PID: $BACKEND_PID) 在: http://localhost:5000${NC}"
}

# 定义一个函数以启动前端服务
start_frontend() {
    echo -e "${YELLOW}启动前端服务...${NC}"
    cd /workspace/frontend || exit 1 # Exit if cd fails

    # 检查 npm 命令是否存在
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}错误: npm 命令未找到。请确保 Node.js 和 npm 已在容器中正确安装并配置在 PATH 环境变量中。${NC}"
        # 由于前端无法启动，不清空 FRONTEND_PID 或设置为空
        FRONTEND_PID=""
        # 可以选择在这里退出脚本，如果前端是必需的
        # exit 1
    else
        echo -e "${YELLOW}正在启动前端开发服务器 (npm run dev)...${NC}"
        npm run dev &
        FRONTEND_PID=$! # 保存前端进程的PID
        echo -e "${GREEN}前端服务已启动 (PID: $FRONTEND_PID) 在: http://localhost:3000${NC}"
    fi
}

echo -e "${YELLOW}正在启动WebArt应用...${NC}"

# 启动所有服务
start_backend
start_frontend

echo -e "${GREEN}所有服务已启动!${NC}"
echo -e "${YELLOW}前端: ${NC}${FRONTEND_PID:+http://localhost:3000 (PID: $FRONTEND_PID) - }${FRONTEND_PID:+${GREEN}'运行中'${NC}}${FRONTEND_PID:-${RED}'启动失败/未启动'${NC}}"
echo -e "${YELLOW}后端API: ${NC}${BACKEND_PID:+http://localhost:5000 (PID: $BACKEND_PID) - }${GREEN}${BACKEND_PID:+'运行中'}${NC}"
echo -e "${YELLOW}按Ctrl+C停止所有服务${NC}"

# 等待任何一个后台进程结束。如果任何一个进程异常退出，脚本也会退出。
# cleanup 函数会确保在脚本退出时（包括Ctrl+C）杀死另一个进程。
wait -n
# 如果 wait -n 因为信号中断退出（例如 Ctrl+C），trap 会接管
# 如果是因为某个进程自己退出了，我们也调用 cleanup 来关闭另一个
cleanup 