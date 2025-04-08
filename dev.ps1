#!/usr/bin/env pwsh
# WebArt开发环境启动脚本

Write-Host "正在启动WebArt开发环境..." -ForegroundColor Green

# 确保必要的目录存在
if (-not (Test-Path ./backend/data)) {
    New-Item -ItemType Directory -Path ./backend/data -Force | Out-Null
    Write-Host "创建了 backend/data 目录" -ForegroundColor Cyan
}

if (-not (Test-Path ./backend/static/uploads)) {
    New-Item -ItemType Directory -Path ./backend/static/uploads -Force | Out-Null
    Write-Host "创建了 backend/static/uploads 目录" -ForegroundColor Cyan
}

if (-not (Test-Path ./frontend/public)) {
    New-Item -ItemType Directory -Path ./frontend/public -Force | Out-Null
    Write-Host "创建了 frontend/public 目录" -ForegroundColor Cyan
}

# 停止并移除之前的容器
Write-Host "停止现有容器..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml -f .devcontainer/docker-compose.extend.yml down 2>$null

# 构建并启动开发环境
Write-Host "构建并启动容器..." -ForegroundColor Cyan
docker-compose -f docker-compose.dev.yml -f .devcontainer/docker-compose.extend.yml up --build -d

# 显示容器状态
Write-Host "`n容器状态:" -ForegroundColor Green
docker-compose -f docker-compose.dev.yml -f .devcontainer/docker-compose.extend.yml ps

Write-Host "`nWebArt开发环境已启动!" -ForegroundColor Green
Write-Host "前端: http://localhost" -ForegroundColor Cyan
Write-Host "后端API: http://localhost/api" -ForegroundColor Cyan
Write-Host "要查看日志，请运行: docker-compose -f docker-compose.dev.yml -f .devcontainer/docker-compose.extend.yml logs -f" -ForegroundColor Yellow
Write-Host "要停止环境，请运行: docker-compose -f docker-compose.dev.yml -f .devcontainer/docker-compose.extend.yml down" -ForegroundColor Yellow 