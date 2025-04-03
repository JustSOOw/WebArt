'''
Author: JustSOOw wang813104@outlook.com
Date: 2025-03-10 13:45:37
LastEditors: AI Assistant
LastEditTime: 2025-03-22 12:15:00
FilePath: /WebArt/backend/app/api/uploads.py
Description: 文件上传API

Copyright (c) 2025 by Furdow, All Rights Reserved. 
'''
import os
import uuid
import time
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app.utils import allowed_image_file, allowed_font_file, save_uploaded_file, validate_image, clean_exif
from PIL import Image # type: ignore

uploads_bp = Blueprint('uploads', __name__)

@uploads_bp.route('/upload', methods=['POST'])
def upload_image():
    """
    上传参考图片
    """
    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['file']
    
    # 检查文件名
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    # 检查文件类型
    if not allowed_image_file(file.filename):
        return jsonify({'error': '不支持的文件类型，请上传jpg/png/jpeg/bmp格式的图片'}), 400
    
    try:
        # 保存文件
        file_url = save_uploaded_file(file, 'images')
        
        # 获取文件的绝对路径
        file_path = os.path.join(
            current_app.root_path, 
            'static/uploads/images', 
            os.path.basename(file_url.split('/')[-1])
        )
        
        # 验证图片
        is_valid, width, height, error_msg = validate_image(file_path)
        if not is_valid:
            # 删除无效文件
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({'error': error_msg}), 400
        
        # 清除EXIF数据
        if file.filename.lower().endswith(('.jpg', '.jpeg')):
            clean_exif(file_path)
        
        return jsonify({
            'url': file_url,
            'width': width,
            'height': height
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"文件上传失败: {str(e)}")
        return jsonify({'error': f'文件上传失败: {str(e)}'}), 500

@uploads_bp.route('/upload-ttf', methods=['POST'])
def upload_font():
    """
    上传自定义字体文件
    """
    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['file']
    
    # 检查文件名
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    # 检查文件类型
    if not allowed_font_file(file.filename):
        return jsonify({'error': '不支持的文件类型，请上传ttf/otf格式的字体文件'}), 400
    
    try:
        # 保存文件
        file_url = save_uploaded_file(file, 'fonts')
        
        # 获取字体名称
        font_name = os.path.splitext(os.path.basename(file.filename))[0]
        
        return jsonify({
            'url': file_url,
            'name': font_name
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"字体上传失败: {str(e)}")
        return jsonify({'error': f'字体上传失败: {str(e)}'}), 500

@uploads_bp.route('/chat/upload', methods=['POST'])
def chat_upload_file():
    """
    聊天API的文件上传（图片/音频/视频）
    """
    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['file']
    
    # 检查文件名
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    # 获取文件类型
    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1].lower()
    
    # 根据文件类型确定子目录
    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
        subdir = 'chat_images'
        media_type = 'image'
        max_size = 10 * 1024 * 1024  # 10MB
        
        # 验证图片尺寸
        try:
            img = Image.open(file)
            width, height = img.size
            
            # 检查图片尺寸是否符合要求
            if width < 10 or height < 10:
                return jsonify({'error': '图片尺寸太小，宽度和高度必须大于10像素'}), 400
            
            # 检查宽高比
            ratio = max(width/height, height/width)
            if ratio > 200:
                return jsonify({'error': '图片宽高比异常，不应超过200:1或1:200'}), 400
        except Exception as e:
            return jsonify({'error': f'无效的图片文件: {str(e)}'}), 400
        
    elif ext in ['.mp3', '.wav', '.m4a', '.ogg']:
        subdir = 'chat_audio'
        media_type = 'audio'
        max_size = 10 * 1024 * 1024  # 10MB
        
    elif ext in ['.mp4', '.webm', '.mov']:
        subdir = 'chat_video'
        media_type = 'video'
        max_size = 150 * 1024 * 1024  # 150MB
        
    else:
        return jsonify({'error': '不支持的文件类型'}), 400
    
    # 检查文件大小
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > max_size:
        size_mb = max_size / (1024 * 1024)
        return jsonify({'error': f'文件大小超过限制 ({size_mb:.0f}MB)'}), 400
    
    try:
        # 创建目录（如果不存在）
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], subdir)
        os.makedirs(upload_folder, exist_ok=True)
        
        # 生成唯一的文件名
        timestamp = int(time.time())
        unique_filename = f"{timestamp}_{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(upload_folder, unique_filename)
        
        # 保存文件
        file.save(file_path)
        
        # 如果是图片，清除EXIF数据
        if media_type == 'image' and ext in ['.jpg', '.jpeg']:
            clean_exif(file_path)
        
        # 生成URL
        file_url = f"/api/uploads/{subdir}/{unique_filename}"
        
        return jsonify({
            'url': file_url,
            'media_type': media_type,
            'file_name': filename,
            'file_size': file_size
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"文件上传失败: {str(e)}")
        return jsonify({'error': f'文件上传失败: {str(e)}'}), 500

@uploads_bp.route('/uploads/<path:subdir>/<filename>', methods=['GET'])
def serve_chat_uploads(subdir, filename):
    """
    提供聊天上传文件的访问
    """
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], subdir)
    return send_from_directory(upload_folder, filename)

@uploads_bp.route('/static/uploads/<path:filename>', methods=['GET'])
def serve_uploads(filename):
    """
    提供上传文件的访问
    """
    return send_from_directory(os.path.join(current_app.root_path, 'static/uploads'), filename)

@uploads_bp.route('/static/<path:filename>', methods=['GET'])
def serve_static(filename):
    """
    提供静态文件的访问
    """
    return send_from_directory(os.path.join(current_app.root_path, 'static'), filename) 