'''
Author: JustSOOw wang813104@outlook.com
Date: 2025-03-10 13:45:37
LastEditors: AI Assistant
LastEditTime: 2025-03-22 12:10:00
FilePath: /WebArt/backend/app/api/__init__.py
Description: API路由注册

Copyright (c) 2025 by Furdow, All Rights Reserved. 
'''
from flask import Blueprint

# 导入蓝图
from app.api.wordart import wordart_bp
from app.api.auth import auth_bp
from app.api.uploads import uploads_bp
from app.api.chat import chat_bp
from app.api.images import images_bp