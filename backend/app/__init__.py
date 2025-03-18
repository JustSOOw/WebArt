r'''
 * @Author: JustSOOw wang813104@outlook.com
 * @Date: 2025-03-10 11:36:13
 * @LastEditors: JustSOOw wang813104@outlook.com
 * @LastEditTime: 2025-03-17 17:58:25
 * @FilePath: \WebArt\backend\app\__init__.py
 * @Description: 
 * @
 * @Copyright (c) 2025 by Furdow, All Rights Reserved. 
'''
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS  # type: ignore # 用于处理跨域资源共享(CORS)
from flask_login import LoginManager  # 用于处理用户认证和会话管理
from dotenv import load_dotenv  # 用于从.env文件加载环境变量

# 加载环境变量
load_dotenv()

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # 配置应用
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///wordart.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DASHSCOPE_API_KEY'] = os.environ.get('DASHSCOPE_API_KEY', '')
    app.config['MAX_CONTENT_LENGTH'] = 30 * 1024 * 1024  # 30MB 最大上传限制
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
    
    # 确保上传目录存在
    #os.path.join来构建文件路径，app.config['UPLOAD_FOLDER']是上传文件的根目录
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'images'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'fonts'), exist_ok=True)
    
    # 初始化扩展，配置CORS以允许跨域请求
    #所有以/api/开头的请求都允许来自http://localhost:3000和http://127.0.0.1:3000的请求
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}}, supports_credentials=True)
    #init_app均是从扩展中导入的，app是Flask应用实例
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # 设置登录视图
    #auth.login是auth蓝图中的login视图函数
    login_manager.login_view = 'auth.login'
    
    # 注册蓝图
    from app.api.auth import auth_bp
    from app.api.wordart import wordart_bp
    from app.api.uploads import uploads_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(wordart_bp, url_prefix='/api')
    app.register_blueprint(uploads_bp, url_prefix='/api')
    
    return app 