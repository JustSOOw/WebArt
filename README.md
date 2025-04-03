# WebArt锦书 - AI创意助手

WebArt锦书是一个基于Vue.js和Flask的Web应用程序，提供AI驱动的对话、图像生成和文本处理功能。该应用使用Docker进行容器化部署，便于开发和生产环境的一致性。

## 功能特点

- AI对话：基于通义千问等大语言模型的智能对话功能
- 多模态支持：支持图片、音频、视频、文档等多种内容格式
- 用户认证：完整的用户注册、登录和授权系统
- 会话管理：保存和管理历史对话
- 响应式设计：适配各种设备屏幕尺寸

## 更新日志

### 2025-03-30更新 (重点)
- **修复了后端核心错误 (500 - NoneType is not iterable)**：解决了在处理多模态消息（尤其是多图片）时，后端 `/api/chat/completions` 路由因未能正确处理 `messages` 数组及其内部元素类型，导致尝试迭代 `None` 而崩溃的问题。通过在路由处理早期阶段添加对 `messages` 列表及其元素的类型检查（确保是列表和字典）来修复。
- **实现了多图片上传功能**: 前端现在支持选择最多10张图片，并通过Base64编码直接发送给AI API。
- **完善了文件上传验证**: 在前端 `ChatInput` 组件的 `beforeUpload` 钩子中添加了更严格的验证，包括：
    - 多图片上传仅限图片类型，且最多10张。
    - 对所有上传的图片、音频、视频文件执行大小、尺寸（图片）、时长（音视频）的限制检查。
- **改进了多图片消息显示与存储**: 多图片消息现在会将文件信息列表存储到IndexedDB，并在消息列表中显示文件数量和名称（但不存储或显示Base64预览）。
- **修复了输入框UI问题**: 解决了文件名遮挡输入文本、光标显示异常等问题，通过优化布局和使用透明覆盖输入框实现。
- **移除了调试日志**: 清理了前后端代码中用于排查问题的临时日志。

### 2025-03-25更新
- 修复了后端配置问题，解决了应用初始化错误
- 优化了上传功能，支持多文件上传
- 改进了文件上传UI，显示多文件选择状态
- 优化了后端存储目录，自动创建必要的文件夹
- 添加了文本与文件必须同时发送的限制，防止单独发送文件
- 修复了500错误和502错误，提升了服务稳定性

## 技术栈

### 前端
- Vue.js 3 (组合式API)
- Vue Router 4
- Element Plus UI库
- Vite构建工具
- Axios HTTP客户端

### 后端
- Flask框架
- Flask-SQLAlchemy (ORM)
- Flask-Login (身份验证)
- Flask-Migrate (数据库迁移)
- JWT认证

### 部署
- Docker & Docker Compose
- Nginx反向代理
- SQLite数据库

## 项目结构

```
WebArt/
├── frontend/             # 前端Vue.js项目
│   ├── src/              # 源代码
│   │   ├── api/          # API调用
│   │   ├── assets/       # 静态资源
│   │   ├── components/   # Vue组件
│   │   ├── router/       # 路由定义
│   │   ├── store/        # 状态管理
│   │   ├── utils/        # 工具函数
│   │   ├── views/        # 页面视图
│   │   ├── App.vue       # 根组件
│   │   └── main.js       # 入口文件
│   ├── Dockerfile.dev    # 开发环境Dockerfile
│   └── Dockerfile.build  # 生产环境Dockerfile
├── backend/              # 后端Flask项目
│   ├── app/              # 应用代码
│   │   ├── api/          # API路由
│   │   ├── models/       # 数据模型
│   │   ├── services/     # 业务逻辑
│   │   ├── static/       # 静态文件
│   │   └── utils/        # 工具函数
│   ├── data/             # 数据存储目录
│   ├── migrations/       # 数据库迁移文件
│   ├── .env              # 环境变量配置
│   ├── Dockerfile        # 生产环境Dockerfile
│   └── Dockerfile.dev    # 开发环境Dockerfile
├── nginx/                # Nginx配置
├── docker-compose.yml    # 生产环境配置
├── docker-compose.dev.yml # 开发环境配置
├── cleanup.ps1           # Docker资源清理脚本
└── dev.ps1               # 开发环境启动脚本
```

## 开发设置

### 快速开始

1. 克隆仓库
2. 确保已安装Docker和Docker Compose
3. 使用PowerShell运行开发脚本:

```
./dev.ps1
```

开发服务会在以下地址启动:
- 前端: http://localhost
- 后端API: http://localhost/api

### 使用VS Code Dev Containers开发

项目支持使用VS Code Dev Containers进行开发，提供隔离且一致的开发环境：

1. 安装[VS Code](https://code.visualstudio.com/)和[Dev Containers扩展](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. 在VS Code中打开项目根目录
3. 点击左下角绿色图标，选择"Reopen in Container"
4. 等待容器构建完成，VS Code将在容器内打开项目
5. 所有必要的扩展和工具已预先配置好

详细说明请参考`.devcontainer/README.md`文件。

### Docker资源优化

为避免Docker占用过多磁盘空间，项目包含以下优化:

1. 使用`.dockerignore`文件排除不必要的构建上下文文件
2. 使用`tmpfs`卷挂载减少非永久数据的磁盘写入
3. 优化Dockerfile减少构建层数和缓存大小
4. 提供资源清理脚本`cleanup.ps1`用于定期清理

当Docker磁盘空间占用过大时，可使用以下命令清理:

```
./cleanup.ps1
```

## API文档

主要API端点:

- `/api/auth/*` - 用户认证
- `/api/chat/*` - 对话功能
- `/api/images/*` - 图像生成
- `/api/wordart/*` - 文本处理

## 常见问题

1.  **后端返回 500 错误 (`Internal Server Error`)**: 
    *   **可能原因 1 (已修复)**: 如果错误信息类似 `argument of type 'NoneType' is not iterable` 或涉及对 `None` 的操作，这通常发生在 `/api/chat/completions` 路由处理传入的 `messages` 列表时。旧版本代码可能未能正确处理 `messages` 列表为空、包含非字典项，或未能正确处理多模态消息中 `content` 为数组的情况。**解决方法**: 确保您运行的是最新代码，其中已添加对 `messages` 及其元素的类型和结构的健壮性检查。
    *   **其他原因**: 检查后端容器日志 (`docker logs <backend_container_name>`) 获取详细错误信息。可能是数据库连接问题、依赖项错误、AI服务调用失败等。
2.  如遇到 **502 Bad Gateway** 错误，请检查后端服务 (`docker ps` 查看状态) 和 Nginx 代理配置 (`nginx/nginx.dev.conf`) 是否正常，查看后端和 Nginx 日志。
3.  **上传文件失败 (413 Request Entity Too Large)**: 当上传大文件或多张图片时，请求的总大小可能超过了 Nginx 的限制 (`client_max_body_size`)。前端虽然有单文件大小限制，但多文件 Base64 编码后的总大小也可能超限。检查 `nginx/nginx.dev.conf` 中的 `client_max_body_size` 设置，并考虑是否需要增加。同时，前端的文件大小验证逻辑也在不断完善中。
4.  数据库问题可参考 `backend/DB_README.md`。
5.  如果构建过程变慢或Docker占用空间过大，运行 `cleanup.ps1` 清理资源。

