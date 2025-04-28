# WebArt 生产环境部署指南

本文档指导您如何在服务器上部署 WebArt 应用的生产环境。

## 部署准备

在部署应用前，请确保您的服务器满足以下条件：

- **操作系统**: Linux (推荐 Ubuntu, CentOS, Debian)
- **已安装 Docker**: 版本 20.10.0 或更高 (参考 [Docker 官方安装文档](https://docs.docker.com/engine/install/))
- **已安装 Docker Compose (V2 Plugin)**: 版本 2.0.0 或更高 (参考 [Docker Compose 官方安装文档](https://docs.docker.com/compose/install/)). **注意**: 使用 `docker compose` 命令（无连字符）。
- **公网 IP 地址**: 服务器需要有一个公网 IP。
- **域名**: 您需要一个域名，并将其 DNS A 记录指向您服务器的公网 IP。
- **防火墙/安全组**: 确保服务器的防火墙或云服务商（如阿里云）的安全组允许 **入站** 流量访问端口 `80` (HTTP) 和 `443` (HTTPS)。同时，确保 **出站** 流量允许访问 HTTPS (端口 `443`)，以便拉取 Docker 镜像和 Python 包。

## 文件准备

1.  **上传项目代码**: 使用 `git clone` 或 `scp`/`sftp` 将整个 `WebArt` 项目文件夹上传到您的服务器（例如 `/home/your_user/WebArt` 或 `/var/www/webart`）。
2.  **创建 `.env` 文件**: 在项目根目录下（与 `docker-compose.yml` 同级）创建一个名为 `.env` 的文件。复制 `.env.example` 的内容到 `.env`，并根据您的生产环境配置修改变量，特别是数据库配置、`SECRET_KEY` 以及 **正确的** `PUBLIC_BASE_URL` (格式：`https://yourdomain.com`)。
3.  **替换 Nginx 配置中的域名**: 编辑 `nginx/nginx.conf` 文件，将所有 `yourdomain.com` 的占位符替换为您**实际使用的域名**。

## SSL 证书获取 (Let's Encrypt / Certbot)

本配置使用 Certbot 自动获取和更新免费的 Let's Encrypt SSL 证书。**首次部署时必须按以下顺序操作**：

1.  **准备 Nginx (HTTP-only模式)**:
    *   编辑 `nginx/nginx.conf` 文件。
    *   **注释掉**整个 `server { listen 443 ssl; ... }` 的 HTTPS 服务器块。
    *   **注释掉** HTTP 服务器块 (`server { listen 80; ... }`) 中 `location / { ... }` 内部的 `return 301 https://$host$request_uri;` 这一行，以**禁用** HTTP 到 HTTPS 的重定向。
    *   确保 HTTP 服务器块中用于 Certbot 验证的 `location /.well-known/acme-challenge/ { ... }` 块**没有**被注释掉。
    *   保存文件。

2.  **启动 Nginx 服务 (仅 HTTP)**:
    ```bash
    # 确保在项目根目录下
    sudo docker compose up -d nginx
    ```
    *检查状态: `sudo docker compose ps nginx`，确保其正在运行。*

3.  **运行 Certbot 获取证书**:
    ```bash
    # 将 yourdomain.com 替换为您的域名，如果需要 www 子域，可以添加 -d www.yourdomain.com
    sudo docker compose run --rm certbot certonly --webroot -w /var/www/certbot -d yourdomain.com
    ```
    *按照提示输入邮箱并同意条款。如果成功，证书将保存在 `./certbot/conf` 目录下。*
    *如果失败，请检查 DNS 是否已指向服务器 IP、端口 80 是否开放、Nginx 服务是否正在运行以及 `nginx.conf` 中 `server_name` 是否正确。*

4.  **恢复 Nginx 配置 (启用 HTTPS)**:
    *   编辑 `nginx/nginx.conf` 文件。
    *   **取消注释**整个 `server { listen 443 ssl; ... }` 的 HTTPS 服务器块。
    *   **取消注释** HTTP 服务器块中的 `return 301 https://$host$request_uri;` 行，以**启用** HTTP 到 HTTPS 的重定向。
    *   保存文件。

5.  **重启 Nginx 应用完整配置**:
    ```bash
    sudo docker compose restart nginx
    ```

## 首次部署应用

在完成 SSL 证书首次获取并恢复 Nginx 配置后，执行以下步骤启动整个应用：

1.  **构建并启动所有服务**:
    ```bash
    # 确保在项目根目录下
    sudo docker compose up -d --build
    ```
    *`--build` 会根据 Dockerfile 构建镜像。首次构建可能需要一些时间。*

2.  **检查服务状态**: 确保所有服务都已成功启动并且状态为 `Up` 或 `Running`。
    ```bash
    sudo docker compose ps
    ```

3.  **检查日志**: 查看是否有任何启动错误。
    ```bash
    # 查看所有服务日志
    sudo docker compose logs
    # 查看特定服务日志（例如 backend）
    sudo docker compose logs backend
    ```

现在，您应该可以通过 `https://yourdomain.com` 访问您的 WebArt 应用了。

## 更新应用

当您更新了代码后，部署更新通常很简单：

1.  **获取最新代码**: 如果使用 Git，在服务器的项目目录下运行：
    ```bash
    git pull
    ```
    *如果手动上传，请覆盖相应文件。*

2.  **重新构建并重启服务**: Docker Compose 会自动识别哪些服务的镜像需要重新构建。
    ```bash
    # 确保在项目根目录下
    sudo docker compose up -d --build
    ```
    *有时，如果依赖未变，可能只需要 `sudo docker compose restart <service_name>` 或 `sudo docker compose up -d`。*

## 数据持久化

应用的关键数据存储在 Docker 命名卷中，以确保在容器重建后数据不会丢失：

-   `frontend_build`: (理论上不需要持久化，因为每次构建都会生成) - Nginx 使用的静态文件。
-   `backend_data`: 后端 SQLite 数据库文件 (位于 `/app/data`)。
-   `backend_static`: 用户上传的静态文件 (位于 `/app/static`)。
-   `./certbot/conf`: Let's Encrypt 的证书和账户信息。
-   `./certbot/www`: Certbot 用于 HTTP-01 验证的临时文件。

建议定期备份 `./certbot/conf` 目录以及通过 Docker 命令备份 `backend_data` 和 `backend_static` 卷。

## 故障排除

-   **无法访问应用**: 检查 DNS 解析、阿里云/服务器防火墙（入站 80/443）、Nginx 容器状态和日志。
-   **静态文件 404**: 检查 `nginx.conf` 中的 `root` 和 `alias` 路径是否正确，检查 `backend_static` 卷是否正确挂载到 Nginx 容器。
-   **API 错误**: 检查 `backend` 容器日志 (`sudo docker compose logs backend`)。
-   **Docker 镜像拉取失败/超时**: 检查服务器网络连接（特别是出站 HTTPS），考虑配置国内 Docker 镜像加速器（修改 `/etc/docker/daemon.json` 并重启 Docker 服务）。
-   **Python 包安装失败**: 检查服务器网络连接，考虑在 `backend/Dockerfile` 的 `pip install` 命令中添加 `-i` 参数使用国内 PyPI 镜像源。
-   **Certbot 失败**: 确认 DNS 已生效、端口 80 已开放、Nginx（HTTP-only 模式）正在运行、`server_name` 配置正确。

## 性能优化建议

-   在 `backend/Dockerfile` 中调整 Gunicorn 的 `--workers` 数量（通常是 `2 * CPU核心数 + 1`）。
-   在 `nginx.conf` 中启用 `gzip on;` 及相关配置。
-   考虑使用 CDN 加速静态资源。

## 安全建议

-   定期更新服务器操作系统、Docker、Docker Compose 及所有应用依赖。
-   保持防火墙/安全组规则最小化，仅开放必要端口。
-   确保 `.env` 文件权限安全，不要提交到 Git 仓库。
-   定期备份数据。 