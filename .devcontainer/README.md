# WebArt锦书 Dev Containers开发指南

本目录包含了使用VS Code Dev Containers扩展在容器化环境中开发WebArt锦书应用的配置文件。

## 前提条件

- 已安装[Docker Desktop](https://www.docker.com/products/docker-desktop)
- 已安装[Visual Studio Code](https://code.visualstudio.com/)或[Cursor](https://cursor.sh/)
- 已安装[Dev Containers扩展](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

## 使用方法

1. 在VS Code或Cursor中打开WebArt项目根目录
2. 点击左下角的绿色图标，或按`Ctrl+Shift+P`打开命令面板
3. 输入并选择`Dev Containers: Reopen in Container`
4. VS Code/Cursor将根据配置文件构建开发容器，这可能需要几分钟时间
5. 容器启动后，你将在容器内部的开发环境中工作

## 在Dev Containers中运行项目

容器构建完成后，有两种方式可以启动项目：

### 方法1：使用启动脚本（推荐）

1. 打开终端（`Ctrl+``或菜单栏的"终端 > 新建终端"）
2. 运行启动脚本：
```bash
bash /workspace/start-services.sh
```
3. 脚本会自动启动后端和前端服务
4. 在浏览器中访问：
   - 前端：http://localhost:3000
   - 后端API：http://localhost:5000/api

### 方法2：分别启动服务

如果你想单独控制各个服务，可以：

1. 启动后端服务：
```bash
cd /workspace/backend
python init_db.py
python -m flask run --host=0.0.0.0 --port=5000
```

2. 在新终端启动前端服务：
```bash
cd /workspace/frontend
npm install
npm run dev
```

3. 在浏览器中访问：
   - 前端：http://localhost:3000
   - 后端API：http://localhost:5000/api

## 文件挂载和同步说明

### 挂载方式

- 整个项目目录通过**绑定挂载(bind mount)**的方式挂载到容器中的`/workspace`目录
- 这意味着本地文件系统和容器内的`/workspace`目录共享相同的文件

### 文件同步

- **双向同步**：在容器内修改文件会立即反映到本地文件系统，反之亦然
- **Git操作**：所有Git相关文件(`.git`目录等)也被挂载到容器中，可以在容器内执行Git操作
- **挂载选项**：使用`:cached`挂载选项可以提高性能，尤其是在Windows和macOS上

### 文件存储位置

- **挂载的文件**：存储在本地机器上，容器只是提供一个访问窗口
- **容器内生成的文件**：如果保存在`/workspace`目录中，将自动同步到本地
- **临时文件**：保存在容器内其他目录的文件在容器销毁时会丢失

### 文件权限

- 容器内使用root用户，这对于开发环境简化了权限管理
- 在容器内创建的文件可能在本地属于不同的用户/组，这是正常的

## 环境配置说明

- 使用`python:3.11-slim-bullseye`作为基础镜像，避免使用Alpine镜像，因为VS Code Server在Alpine环境下可能存在兼容性问题
- 使用root用户运行容器，简化权限管理
- 项目目录结构：
  ```
  /workspace/        # 整个项目目录
  ├── frontend/      # 前端代码
  ├── backend/       # 后端代码
  ├── nginx/         # Nginx配置
  ├── .git/          # Git仓库数据
  └── .devcontainer/ # 开发容器配置
  ```

## 开发工作流

- 主要代码在后端容器中打开
- 可以通过终端访问容器内环境
- 端口映射已配置，你可以在浏览器中访问:
  - 前端: http://localhost:3000（在容器内运行时）
  - 后端API: http://localhost:5000/api（在容器内运行时）


前端服务：

```bash
cd /workspace/frontend
npm install
npm run dev
```

## 切换开发容器

开发环境配置了连接到后端容器。如果需要在前端容器中工作，可以：

1. 点击左下角绿色图标
2. 选择`Attach to Running Container...`
3. 选择`webart-frontend-dev-1`容器

## 扩展开发容器

如需添加更多工具或依赖，可以：

1. 修改`.devcontainer/devcontainer.json`添加扩展
2. 修改`.devcontainer/docker-compose.extend.yml`更改容器配置
3. 执行`Dev Containers: Rebuild Container`应用更改 