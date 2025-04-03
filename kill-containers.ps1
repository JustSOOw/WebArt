Write-Host "正在停止所有Docker容器..." -ForegroundColor Yellow
docker stop $(docker ps -q)

Write-Host "正在移除所有Docker容器..." -ForegroundColor Yellow
docker rm $(docker ps -a -q)

Write-Host "正在清理未使用的Docker资源..." -ForegroundColor Yellow
docker system prune -f

Write-Host "端口使用情况:" -ForegroundColor Green
netstat -ano | findstr "LISTENING" | findstr "80 3000 5000"

Write-Host "清理完成!" -ForegroundColor Green 