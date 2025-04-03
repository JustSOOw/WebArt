r'''
 * @Author: JustSOOw wang813104@outlook.com
 * @Date: 2025-03-10 11:37:34
 * @LastEditors: AI Assistant
 * @LastEditTime: 2025-03-22 12:20:00
 * @FilePath: \WebArt\backend\app\utils\file_utils.py
 * @Description: 文件处理工具函数
 * @
 * @Copyright (c) 2025 by Furdow, All Rights Reserved. 
'''
import os
import uuid
import requests
import io
from flask import current_app
from werkzeug.utils import secure_filename
from PIL import Image as PILImage   # type: ignore

def allowed_image_file(filename):
    """
    检查文件是否为允许的图片类型
    """
    allowed_extensions = {'png', 'jpg', 'jpeg', 'bmp', 'gif'}
    # 检查文件名是否包含点而且判断以点分割后的后缀是否在allowed_extensions中
    #rsplit('.', 1)[1].lower()以点分割，1表示只分割一次，[1]表示分割后第二个元素，lower()表示转换为小写
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def allowed_font_file(filename):
    """
    检查文件是否为允许的字体类型
    """
    allowed_extensions = {'ttf', 'otf'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def allowed_audio_file(filename):
    """
    检查文件是否为允许的音频类型
    """
    allowed_extensions = {'mp3', 'wav', 'm4a', 'ogg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def allowed_video_file(filename):
    """
    检查文件是否为允许的视频类型
    """
    allowed_extensions = {'mp4', 'webm', 'mov'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, subfolder):
    """
    保存上传的文件
    """
    # 确保上传目录存在
    #os.path.join拼接路径
    upload_folder = os.path.join(current_app.root_path, 'static/uploads', subfolder)
    os.makedirs(upload_folder, exist_ok=True)
    
    # 生成安全的文件名
    filename = secure_filename(file.filename)
    # 添加随机字符串，避免文件名冲突
    random_prefix = uuid.uuid4().hex[:8]
    filename = f"{random_prefix}_{filename}"
    
    # 保存文件
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    # 返回可访问的URL
    return f"/api/static/uploads/{subfolder}/{filename}"

def clean_exif(file_path):
    """
    清除图片的EXIF数据
    
    Args:
        file_path: 图片文件路径
        
    Returns:
        bool: 是否成功清除EXIF数据
    """
    try:
        # 打开图片
        img = PILImage.open(file_path)
        
        # 创建一个新的空白图片，与原图大小和模式相同
        data = list(img.getdata())
        image_without_exif = PILImage.new(img.mode, img.size)
        image_without_exif.putdata(data)
        
        # 保存没有EXIF的图片
        image_without_exif.save(file_path)
        return True
    except Exception as e:
        current_app.logger.error(f"清除EXIF数据失败: {str(e)}")
        return False

def validate_image(file_path):
    """
    验证图片是否有效以及获取尺寸
    """
    try:
        with PILImage.open(file_path) as img:
            width, height = img.size
            
            # 检查尺寸是否合理
            if width <= 0 or height <= 0:
                return False, None, None, "图片尺寸无效"
            
            # 检查宽高比是否合理
            aspect_ratio = max(width/height, height/width)
            if aspect_ratio > 200:
                return False, None, None, "图片宽高比异常，不应超过200:1或1:200"
            
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size > 10 * 1024 * 1024:  # 10MB
                return False, None, None, "图片文件大小不能超过10MB"
            
            return True, width, height, None
    except Exception as e:
        return False, None, None, f"图片验证失败: {str(e)}"

def download_remote_image(url, subfolder='images'):
    """
    下载远程图片并保存到本地
    """
    try:
        # 发送HTTP请求获取图片
        response = requests.get(url, stream=True, timeout=10)
        
        if response.status_code != 200:
            return None, f"下载图片失败，HTTP状态码：{response.status_code}"
        
        # 尝试从Content-Type中获取文件扩展名
        content_type = response.headers.get('Content-Type', '')
        ext = '.jpg'  # 默认扩展名
        
        if 'image/jpeg' in content_type:
            ext = '.jpg'
        elif 'image/png' in content_type:
            ext = '.png'
        elif 'image/gif' in content_type:
            ext = '.gif'
        elif 'image/bmp' in content_type:
            ext = '.bmp'
        
        # 创建一个唯一的文件名
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        
        # 确保目录存在
        upload_folder = os.path.join(current_app.root_path, 'static/uploads', subfolder)
        os.makedirs(upload_folder, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_folder, unique_filename)
        
        # 以二进制方式写入文件
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # 验证下载的文件是否为有效图片
        try:
            with PILImage.open(file_path) as img:
                # 如果能打开，说明文件是有效的图片
                pass
                
            # 清除EXIF数据
            if ext.lower() in ['.jpg', '.jpeg']:
                clean_exif(file_path)
            
            # 返回可访问的URL
            return f"/api/static/uploads/{subfolder}/{unique_filename}", None
            
        except Exception as e:
            # 如果不是有效图片，删除文件并返回错误
            if os.path.exists(file_path):
                os.remove(file_path)
            return None, f"下载的文件不是有效图片: {str(e)}"
        
    except Exception as e:
        return None, f"下载图片失败: {str(e)}"