import jwt # type: ignore
import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册
    """
    data = request.get_json()
    
    # 验证必要字段
    #生成器表达式：如果data中没有username、email、password这三个键，则返回False，否则返回True
    if not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({'error': '缺少必要字段'}), 400
    
    # 检查用户名和邮箱是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '邮箱已存在'}), 400
    
    # 创建新用户
    user = User(
        username=data['username'],
        email=data['email'],
        password=data['password']
    )
    
    db.session.add(user)
    db.session.commit()
    
    # 生成JWT令牌
    token = generate_token(user)
    
    return jsonify({
        'message': '注册成功',
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录
    """
    data = request.get_json()
    
    # 验证必要字段
    if not all(k in data for k in ('username', 'password')):
        return jsonify({'error': '缺少必要字段'}), 400
    
    # 查找用户
    user = User.query.filter_by(username=data['username']).first()
    
    # 验证密码
    if user is None or not user.check_password(data['password']):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    # 更新最后登录时间
    user.last_login = datetime.datetime.utcnow()
    db.session.commit()
    
    # 登录用户
    login_user(user)
    
    # 生成JWT令牌
    token = generate_token(user)
    
    return jsonify({
        'message': '登录成功',
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    })

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    用户登出
    """
    logout_user()
    return jsonify({'message': '登出成功'})

@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """
    获取用户资料
    """
    return jsonify({
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'created_at': current_user.created_at.isoformat(),
            'last_login': current_user.last_login.isoformat() if current_user.last_login else None
        }
    })

def generate_token(user):
    """
    生成JWT令牌
    """
    payload = {
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    
    return jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    ) 