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
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建扩展
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'

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
        
        # 配置上传目录
        app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(app.root_path), 'static', 'uploads')
        
        # 确保上传目录存在
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'images'), exist_ok=True)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'audio'), exist_ok=True)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'video'), exist_ok=True)
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
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    
    return app 