# WordArt锦书 - 后端

这是WordArt锦书百家姓生成应用的后端服务。

## 功能

- 百家姓生成API调用
- 用户认证和授权
- 图片上传和管理
- 历史记录查询

## 技术栈

- Flask
- SQLAlchemy
- Flask-Login
- JWT认证

## 安装和运行

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 配置环境变量

复制`.env.example`文件为`.env`，并填写相应的配置：

```bash
cp .env.example .env
```

3. 初始化数据库

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

4. 运行应用

```bash
flask run
```

## API文档

### 认证API

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/profile` - 获取用户资料

### 百家姓生成API

- `POST /api/generate` - 提交百家姓生成任务
- `GET /api/tasks/<task_id>` - 获取任务状态
- `GET /api/images` - 获取图片列表
- `GET /api/images/<image_id>` - 获取单个图片详情

### 上传API

- `POST /api/upload` - 上传参考图片
- `POST /api/upload-ttf` - 上传TTF字体文件
- `GET /api/static/uploads/<filename>` - 获取上传的文件 