# WebArt锦书 - AI创意助手

WebArt锦书是一个基于Vue.js和Flask的Web应用程序，提供AI驱动的对话、图像生成和文本处理功能。该应用使用Docker进行容器化部署，便于开发和生产环境的一致性。

## 功能特点

- AI对话：基于通义千问等大语言模型的智能对话功能
- 多模态支持：支持图片、音频、视频、文档等多种内容格式
- 用户认证：完整的用户注册、登录和授权系统
- 会话管理：保存和管理历史对话
- 响应式设计：适配各种设备屏幕尺寸

## 更新日志

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

1. 如遇到502错误，请检查后端服务是否正常运行，查看后端日志文件`backend/output.log`
2. 数据库问题可参考`backend/DB_README.md`
3. 如果构建过程变慢或Docker占用空间过大，运行`cleanup.ps1`清理资源
4. 上传文件失败可能是目录权限问题，检查backend/static/uploads目录是否存在且有正确权限
