r'''
 * @Author: JustSOOw wang813104@outlook.com
 * @Date: 2025-03-10 11:36:13
 * @LastEditors: JustSOOw wang813104@outlook.com
 * @LastEditTime: 2025-03-26 19:58:23
 * @FilePath: \WebArt\backend\app\__init__.py
 * @Description: 
 * @
 * @Copyright (c) 2025 by Furdow, All Rights Reserved. 
'''
'''
Author: JustSOOw wang813104@outlook.com
Date: 2025-03-20 11:30:00
LastEditors: AI Assistant
LastEditTime: 2025-03-25 21:30:00
FilePath: /WebArt/backend/app/__init__.py
Description: Flask应用初始化

Copyright (c) 2025 by Furdow, All Rights Reserved. 
'''
import os
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from dotenv import load_dotenv
import jwt # type: ignore
import datetime

# 加载环境变量
load_dotenv()

# 创建扩展
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
# login.login_view = 'auth.login' # 对于纯API和Token认证，通常不需要设置login_view

# --- 添加 request_loader --- 
@login.request_loader
def load_user_from_request(request):
    """Load user from JWT token in Authorization header."""
    auth_header = request.headers.get('Authorization')
    if auth_header:
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == 'bearer':
            token = parts[1]
            try:
                payload = jwt.decode(
                    token,
                    current_app.config['SECRET_KEY'],
                    algorithms=['HS256']
                )
                user_id = payload.get('user_id')
                if user_id:
                    from app.models import User # 延迟导入以避免循环依赖
                    user = User.query.get(user_id)
                    if user:
                        # 可以在这里检查用户是否激活等
                        return user # 返回有效的用户对象
            except jwt.ExpiredSignatureError:
                current_app.logger.warning("Expired JWT token received.")
                return None # Token 已过期
            except jwt.InvalidTokenError:
                current_app.logger.warning("Invalid JWT token received.")
                return None # Token 无效
            except Exception as e:
                current_app.logger.error(f"Error decoding/loading user from token: {e}")
                return None
    # 如果没有有效的 Authorization header 或处理失败，返回 None
    return None

# --- 添加 user_loader --- 
# 即使使用 request_loader，有时也需要 user_loader 来处理某些情况或与其他扩展集成
# 如果 request_loader 已经足够，可以省略 user_loader
# from app.models import User # 如果在这里导入，确保没有循环依赖问题
# @login.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))

def create_app(config_class=None):
    app = Flask(__name__)
    
    # 配置应用
    if config_class:
        app.config.from_object(config_class)
    else:
        # 默认配置
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///wordart.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['DASHSCOPE_API_KEY'] = os.environ.get('DASHSCOPE_API_KEY', '')
        app.config['MAX_CONTENT_LENGTH'] = 30 * 1024 * 1024  # 30MB 最大上传限制
        app.config['PUBLIC_BASE_URL'] = os.environ.get('PUBLIC_BASE_URL', '')  # 添加公开访问URL配置
        
        # 配置上传目录
        app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(app.root_path), 'static', 'uploads')
        
        # 确保上传目录存在
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'images'), exist_ok=True)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'audio'), exist_ok=True)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'videos'), exist_ok=True)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'video_sources'), exist_ok=True)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'documents'), exist_ok=True)
    
    # 初始化CORS
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}}, supports_credentials=True)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    
    # 注册蓝图
    from .api.auth import auth_bp
    from .api.chat import chat_bp
    from .api.wordart import wordart_bp
    from .api.uploads import uploads_bp
    from .api.images import images_bp
    from .api.video import video_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(wordart_bp, url_prefix='/api/wordart')
    app.register_blueprint(uploads_bp, url_prefix='/api/uploads')
    app.register_blueprint(images_bp, url_prefix='/api/images')
    app.register_blueprint(video_bp, url_prefix='/api/video')
    
    return app 