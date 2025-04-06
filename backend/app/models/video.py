'''
Author: JustSOOw wang813104@outlook.com
Date: 2025-04-03 14:30:00
LastEditors: AI Assistant
LastEditTime: 2025-04-03 14:30:00
FilePath: /WebArt/backend/app/models/video.py
Description: 视频生成任务模型

Copyright (c) 2025 by Furdow, All Rights Reserved. 
'''
from datetime import datetime
from app import db

class Video(db.Model):
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(64), index=True)
    video_url = db.Column(db.String(255), nullable=True)  # DashScope返回的URL
    local_path = db.Column(db.String(255), nullable=True)  # 本地存储路径
    prompt = db.Column(db.Text, nullable=False)  # 提示词
    model = db.Column(db.String(50), nullable=False)  # 使用的模型
    type = db.Column(db.String(20), nullable=False)  # text-to-video 或 image-to-video
    
    # 文生视频特有属性
    size = db.Column(db.String(20), nullable=True)  # 分辨率，如"1280*720"
    
    # 图生视频特有属性
    source_image = db.Column(db.String(255), nullable=True)  # 源图像路径
    resolution = db.Column(db.String(10), nullable=True)  # 分辨率档位，如"720P"
    duration = db.Column(db.Integer, nullable=True)  # 视频时长(秒)
    
    # 通用属性
    seed = db.Column(db.Integer, nullable=True)  # 随机种子
    prompt_extend = db.Column(db.Boolean, default=True)  # 是否智能改写
    
    # 任务状态
    status = db.Column(db.String(20), default='PENDING')  # PENDING, RUNNING, SUCCEEDED, FAILED
    error_message = db.Column(db.Text, nullable=True)  # 错误信息
    
    # 时间记录
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    def __repr__(self):
        return f'<Video {self.id} - {self.type} - {self.status}>'
    
    def to_dict(self):
        """转换为字典，用于API响应"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'video_url': self.video_url,
            'prompt': self.prompt,
            'model': self.model,
            'type': self.type,
            'size': self.size,
            'source_image': self.source_image,
            'resolution': self.resolution,
            'duration': self.duration,
            'seed': self.seed,
            'prompt_extend': self.prompt_extend,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'user_id': self.user_id
        } 