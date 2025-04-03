'''
Author: JustSOOw wang813104@outlook.com
Date: 2025-03-20 11:30:00
LastEditors: AI Assistant
LastEditTime: 2025-03-20 11:30:00
FilePath: /WebArt/backend/app/api/images.py
Description: 图像API路由

Copyright (c) 2025 by Furdow, All Rights Reserved. 
'''
import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Image

# 创建蓝图
images_bp = Blueprint('images', __name__)

def allowed_file(filename):
    """检查文件是否允许上传"""
    allowed_extensions = {'png', 'jpg', 'jpeg', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

@images_bp.route('/upload', methods=['POST'])
@login_required
def upload_image():
    """上传图像文件"""
    if 'file' not in request.files:
        return jsonify({"error": "没有文件"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "没有选择文件"}), 400
    
    if file and allowed_file(file.filename):
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        # 生成唯一名称
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # 保存文件
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images')
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # 设置URL
        url = f"/api/images/view/{unique_filename}"
        
        # 创建数据库记录
        image = Image(
            filename=unique_filename,
            url=url,
            user_id=current_user.id,
            prompt="用户上传"
        )
        
        db.session.add(image)
        db.session.commit()
        
        return jsonify({
            "message": "文件上传成功",
            "filename": unique_filename,
            "url": url,
            "id": image.id
        }), 201
    
    return jsonify({"error": "不允许的文件类型"}), 400

@images_bp.route('/view/<filename>', methods=['GET'])
def view_image(filename):
    """查看图像文件"""
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images')
    return send_from_directory(upload_folder, filename)

@images_bp.route('/list', methods=['GET'])
@login_required
def list_images():
    """获取用户上传的图像列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    images = Image.query.filter_by(user_id=current_user.id)\
            .order_by(Image.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        "images": [img.to_dict() for img in images.items],
        "total": images.total,
        "pages": images.pages,
        "current_page": page
    }), 200

@images_bp.route('/<int:image_id>', methods=['DELETE'])
@login_required
def delete_image(image_id):
    """删除图像"""
    image = Image.query.filter_by(id=image_id, user_id=current_user.id).first()
    
    if not image:
        return jsonify({"error": "图像不存在或无权限删除"}), 404
    
    # 尝试删除文件
    try:
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images')
        file_path = os.path.join(upload_folder, image.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        current_app.logger.error(f"删除图像文件失败: {e}")
    
    # 删除数据库记录
    db.session.delete(image)
    db.session.commit()
    
    return jsonify({"message": "图像已删除"}), 200 