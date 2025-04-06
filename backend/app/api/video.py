'''
Author: JustSOOw wang813104@outlook.com
Date: 2025-04-03 15:10:00
LastEditors: AI Assistant
LastEditTime: 2025-04-03 15:10:00
FilePath: /WebArt/backend/app/api/video.py
Description: 视频生成API

Copyright (c) 2025 by Furdow, All Rights Reserved. 
'''
import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app import db, login
from app.models import Video
from app.services.video_service import VideoService
from app.utils import allowed_image_file

video_bp = Blueprint('video', __name__)

@video_bp.route('/text-to-video', methods=['POST'])
def text_to_video():
    """
    文本生成视频API
    
    请求体:
    {
        "model": "wanx2.1-t2v-turbo",  // 必填，模型名称
        "prompt": "一只可爱的小猫在草地上奔跑",  // 必填，提示词
        "size": "1280*720",  // 可选，分辨率
        "seed": 1234567,  // 可选，随机种子
        "prompt_extend": true  // 可选，是否智能改写
    }
    
    响应:
    {
        "success": true,
        "message": "任务已提交",
        "data": {
            "task_id": "xxxx",
            "video_id": 1
        }
    }
    """
    # --- 主动尝试加载用户 ---
    user = login.request_callback(request) # 调用 request_loader
    current_app.logger.info(f"进入 /text-to-video 路由，主动加载用户: {user}, 认证状态: {user.is_authenticated if user else False}")
    # -------------------------
    
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "message": "无效的请求数据"}), 400
    
    # 获取用户ID（如果已加载）
    user_id = user.id if user and user.is_authenticated else None
    current_app.logger.info(f"在 /text-to-video 中获取到的 user_id: {user_id}")
    
    # 创建任务
    service = VideoService()
    video, error = service.create_text_to_video_task(data, user_id)
    
    if error:
        return jsonify({"success": False, "message": error}), 400
    
    return jsonify({
        "success": True,
        "message": "任务已提交",
        "data": {
            "task_id": video.task_id,
            "video_id": video.id
        }
    })

@video_bp.route('/image-to-video', methods=['POST'])
def image_to_video():
    """
    图像生成视频API
    
    表单数据:
    - model: 必填，模型名称
    - prompt: 必填，提示词
    - image: 可选，图片文件（如果没有提供image_url）
    - image_url: 可选，图片URL（如果没有提供image）
    - resolution: 可选，分辨率
    - duration: 可选，视频时长
    - seed: 可选，随机种子
    - prompt_extend: 可选，是否智能改写
    
    响应:
    {
        "success": true,
        "message": "任务已提交",
        "data": {
            "task_id": "xxxx",
            "video_id": 1
        }
    }
    """
    # --- 主动尝试加载用户 ---
    user = login.request_callback(request) # 调用 request_loader
    current_app.logger.info(f"进入 /image-to-video 路由，主动加载用户: {user}, 认证状态: {user.is_authenticated if user else False}")
    # -------------------------
    
    # 处理表单数据
    data = {}
    for key in request.form:
        if key in ['model', 'prompt', 'image_url', 'resolution', 'duration', 'seed', 'prompt_extend']:
            # 处理特殊类型
            if key == 'duration' and request.form[key]:
                data[key] = int(request.form[key])
            elif key == 'seed' and request.form[key]:
                data[key] = int(request.form[key])
            elif key == 'prompt_extend':
                data[key] = request.form[key].lower() == 'true'
            else:
                data[key] = request.form[key]
    
    # 处理图片文件
    image_file = None
    if 'image' in request.files:
        image_file = request.files['image']
        if image_file.filename == '':
            image_file = None
        elif not allowed_image_file(image_file.filename):
            return jsonify({"success": False, "message": "不支持的图片格式"}), 400
    
    # 确保提供了图片文件或图片URL
    if not image_file and 'image_url' not in data:
        return jsonify({"success": False, "message": "必须提供图片文件或图片URL"}), 400
    
    # 获取用户ID（如果已加载）
    user_id = user.id if user and user.is_authenticated else None
    current_app.logger.info(f"在 /image-to-video 中获取到的 user_id: {user_id}")
    
    # 创建任务
    service = VideoService()
    video, error = service.create_image_to_video_task(data, image_file, user_id)
    
    if error:
        return jsonify({"success": False, "message": error}), 400
    
    return jsonify({
        "success": True,
        "message": "任务已提交",
        "data": {
            "task_id": video.task_id,
            "video_id": video.id
        }
    })

@video_bp.route('/task/<task_id>', methods=['GET'])
def check_task(task_id):
    """
    检查任务状态
    
    响应:
    {
        "success": true,
        "data": {
            "task_id": "xxxx",
            "status": "SUCCEEDED",
            "video_url": "https://example.com/video.mp4",
            ...
        }
    }
    """
    if not task_id:
        return jsonify({"success": False, "message": "缺少任务ID"}), 400
    
    # 先从数据库查询任务信息
    video = Video.query.filter_by(task_id=task_id).first()
    if not video:
        return jsonify({"success": False, "message": "任务不存在"}), 404
    
    # 如果任务已完成，直接返回结果
    if video.status in ['SUCCEEDED', 'FAILED']:
        return jsonify({
            "success": True,
            "data": video.to_dict()
        })
    
    # 否则，查询API获取最新状态
    try:
        service = VideoService()
        result = service.check_task_status(task_id)
        
        # 重新查询数据库，获取最新状态
        video = Video.query.filter_by(task_id=task_id).first()
        
        return jsonify({
            "success": True,
            "data": video.to_dict()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"查询任务状态失败: {str(e)}"
        }), 500

@video_bp.route('/video/<int:video_id>', methods=['GET'])
def get_video(video_id):
    """
    获取视频详情
    
    响应:
    {
        "success": true,
        "data": {
            "id": 1,
            "task_id": "xxxx",
            "video_url": "https://example.com/video.mp4",
            ...
        }
    }
    """
    video = Video.query.get_or_404(video_id)
    
    # 如果视频有所有者且当前用户不是所有者，则返回403
    if video.user_id and current_user.is_authenticated and video.user_id != current_user.id:
        return jsonify({"success": False, "message": "无权访问此视频"}), 403
    
    return jsonify({
        "success": True,
        "data": video.to_dict()
    })

@video_bp.route('/my-videos', methods=['GET'])
@login_required
def get_my_videos():
    """
    获取当前用户的视频列表
    
    查询参数:
    - page: 页码，默认1
    - per_page: 每页数量，默认10
    
    响应:
    {
        "success": true,
        "data": {
            "videos": [...],
            "total": 100,
            "pages": 10,
            "current_page": 1
        }
    }
    """
    current_app.logger.info(f"进入 /my-videos 路由，当前用户 ID (来自 login_required): {current_user.id}")
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    service = VideoService()
    videos, total, pages = service.get_user_videos(current_user.id, page, per_page)
    
    return jsonify({
        "success": True,
        "data": {
            "videos": videos,
            "total": total,
            "pages": pages,
            "current_page": page
        }
    })

@video_bp.route('/play/<path:filename>', methods=['GET'])
def play_video(filename):
    """
    获取视频文件
    """
    video_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'videos')
    return send_from_directory(video_dir, filename) 