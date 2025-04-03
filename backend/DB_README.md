# WordArt锦书 - 数据库使用说明

本文档提供了如何初始化和管理WordArt锦书应用数据库的详细说明。

## 数据库结构

WordArt锦书应用使用SQLite数据库，包含以下表：

1. **users** - 用户表
   - id: 用户ID (主键)
   - username: 用户名 (唯一索引)
   - email: 邮箱 (唯一索引)
   - password_hash: 密码哈希
   - created_at: 创建时间
   - last_login: 最后登录时间

2. **images** - 图片表
   - id: 图片ID (主键)
   - task_id: 任务ID (索引)
   - url: 图片URL
   - surname: 姓氏
   - style: 风格代码
   - style_name: 风格名称
   - prompt: 提示词
   - ref_image_url: 参考图URL
   - font_name: 字体名称
   - ttf_url: 字体文件URL
   - text_strength: 文字强度
   - text_inverse: 文字亮暗
   - created_at: 创建时间
   - user_id: 用户ID (外键)

## 初始化数据库

有三种方式可以初始化数据库：

### 方法1: 使用 init_db.py 脚本

这是最简单的方法，直接运行以下命令：

```bash
cd backend
python init_db.py
```

这将创建数据库文件、所有表，并添加一个测试用户。

### 方法2: 使用 Flask-Migrate

这种方法更适合数据库版本管理：

```bash
cd backend
# 设置环境变量
set FLASK_APP=app.py  # Windows
# 或
export FLASK_APP=app.py  # Linux/Mac

# 运行迁移
flask db upgrade
```

### 方法3: 使用管理脚本

管理脚本提供了更多功能：

```bash
cd backend
python manage.py init-db
```

## 管理数据库

管理脚本提供了多种管理数据库的命令：

### 创建管理员用户

```bash
python manage.py create-admin <username> <email> <password>
```

例如：
```bash
python manage.py create-admin admin admin@example.com admin123
```

### 列出所有用户

```bash
python manage.py list-users
```

### 列出最近的图片

```bash
python manage.py list-images --limit 20
```

## 数据库位置

默认情况下，数据库文件位于 `backend/wordart.db`。您可以在 `.env` 文件中修改 `DATABASE_URI` 来更改数据库位置或使用其他数据库系统。

## 备份数据库

SQLite数据库可以通过简单地复制数据库文件来备份：

```bash
# Windows
copy backend\wordart.db backend\wordart.db.backup

# Linux/Mac
cp backend/wordart.db backend/wordart.db.backup
```

## 故障排除

1. **数据库文件不存在**
   - 确保已运行初始化脚本
   - 检查 `.env` 文件中的 `DATABASE_URI` 设置

2. **无法创建表**
   - 确保应用有写入权限
   - 检查数据库模型定义是否正确

3. **迁移错误**
   - 删除 `migrations/versions` 目录中的文件
   - 重新运行 `flask db migrate` 和 `flask db upgrade` 