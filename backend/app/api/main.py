'''
Author: JustSOOw wang813104@outlook.com
Date: 2025-03-20 11:30:00
LastEditors: AI Assistant
LastEditTime: 2025-03-20 11:30:00
FilePath: /WebArt/backend/app/api/main.py
Description: 主API路由

Copyright (c) 2025 by Furdow, All Rights Reserved. 
'''
from flask import Blueprint, jsonify, current_app

# 创建蓝图
main_bp = Blueprint('main', __name__)

@main_bp.route('/status', methods=['GET'])
def get_status():
    """获取API状态"""
    return jsonify({
        "status": "online",
        "version": "1.0.0",
        "features": ["chat", "image-generation"]
    }), 200

@main_bp.route('/config', methods=['GET'])
def get_config():
    """获取公共配置"""
    return jsonify({
        "max_upload_size_mb": current_app.config.get('MAX_CONTENT_LENGTH', 30*1024*1024) // (1024*1024),
        "supported_file_types": [
            "image/jpeg", 
            "image/png", 
            "image/webp"
        ]
    }), 200 