# WebArt 生产环境部署指南

## 部署准备

在部署应用前，请确保您的服务器已经安装了以下软件：

- Docker (版本 20.10.0 或更高)
- Docker Compose (版本 2.0.0 或更高)

## 文件准备

1. 将项目代码上传到服务器
2. 创建 `.env` 文件配置环境变量（参考 `.env.example`）

## SSL证书

本配置支持使用Let's Encrypt获取免费的SSL证书：

1. 首次部署前，禁用HTTPS配置：
   - 编辑 `nginx/nginx.conf`，将HTTPS服务器块注释掉
   - 修改HTTP服务器块，不重定向到HTTPS

2. 初始化证书：
   ```bash
   sudo docker-compose up -d nginx
   sudo docker-compose run --rm certbot certonly --webroot -w /var/www/certbot -d furdow.com -d www.furdow.com
   ```

3. 一旦获取到证书，恢复HTTPS配置（取消注释）并重启服务

## 部署步骤

1. 构建并启动所有服务：
   ```bash
   docker-compose up -d --build
   ```

2. 检查服务状态：
   ```bash
   docker-compose ps
   ```

3. 检查日志确认没有错误：
   ```bash
   docker-compose logs
   ```

## 更新应用

当需要更新应用时，执行以下步骤：

1. 拉取最新代码：
   ```bash
   git pull
   ```

2. 重新构建并启动服务：
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

## 目录结构和数据持久化

应用的数据存储在Docker卷中：

- `frontend_build`: 前端构建产物
- `backend_data`: 后端数据库文件
- `backend_static`: 上传的静态文件

您也可以使用备份脚本定期备份这些卷中的数据。

## 故障排除

1. **无法访问应用**: 检查防火墙是否允许80和443端口
2. **静态文件未加载**: 检查nginx配置和卷挂载
3. **后端API错误**: 查看后端容器日志

## 性能优化

1. 增加Gunicorn工作进程数量（在 `backend/Dockerfile` 中修改）
2. 启用Nginx的gzip压缩
3. 配置CDN加速静态资源

## 安全建议

1. 定期更新Docker镜像和依赖
2. 配置服务器防火墙仅开放必要端口
3. 使用环境变量存储敏感信息，避免硬编码 