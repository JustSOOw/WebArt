r'''
 * @Author: JustSOOw wang813104@outlook.com
 * @Date: 2025-03-10 11:37:34
 * @LastEditors: JustSOOw wang813104@outlook.com
 * @LastEditTime: 2025-03-17 18:17:13
 * @FilePath: \WebArt\backend\app\utils\file_utils.py
 * @Description: 
 * @
 * @Copyright (c) 2025 by Furdow, All Rights Reserved. 
'''
import os
import uuid
import requests
from flask import current_app
from werkzeug.utils import secure_filename
from PIL import Image as PILImage   # type: ignore

def allowed_image_file(filename):
    """
    检查文件是否为允许的图片类型
    """
    allowed_extensions = {'png', 'jpg', 'jpeg', 'bmp'}
    # 检查文件名是否包含点而且判断以点分割后的后缀是否在allowed_extensions中
    #rsplit('.', 1)[1].lower()以点分割，1表示只分割一次，[1]表示分割后第二个元素，lower()表示转换为小写
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def allowed_font_file(filename):
    """
    检查文件是否为允许的字体类型
    """
    allowed_extensions = {'ttf'}
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
    
    # 返回文件URL
    return f"/api/static/uploads/{subfolder}/{filename}"

def validate_image(file_path):
    """
    验证图片文件
    """
    try:
        with PILImage.open(file_path) as img:
            # 检查图片尺寸
            width, height = img.size
            
            # 检查图片是否过大
            if width > 4000 or height > 4000:
                return False, width, height, "图片尺寸过大，请上传小于4000x4000的图片"
            
            # 检查图片是否过小
            if width < 100 or height < 100:
                return False, width, height, "图片尺寸过小，请上传大于100x100的图片"
            
            return True, width, height, None
    except Exception as e:
        return False, 0, 0, f"图片验证失败: {str(e)}"

def download_remote_image(url, subfolder='images'):
    """
    下载远程图片到本地服务器
    
    Args:
        url (str): 远程图片URL
        subfolder (str): 保存的子文件夹
        
    Returns:
        str: 本地图片URL
    """
    try:
        # 如果URL已经是本地URL，直接返回
        if url and url.startswith('/api/static/uploads/'):
            current_app.logger.info(f"URL已经是本地URL，无需下载: {url}")
            return url
        
        current_app.logger.info(f"开始下载远程图片: {url}")
        
        # 确保上传目录存在
        upload_folder = os.path.join(current_app.root_path, 'static/uploads', subfolder)
        os.makedirs(upload_folder, exist_ok=True)
        
        # 从URL下载图片
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        # 检查内容类型
        #get第一个参数是key，第二个参数是默认值
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            current_app.logger.warning(f"下载的内容不是图片: {content_type}")
        
        # 从URL中提取文件名，如果无法提取则生成随机文件名
        try:
            filename = os.path.basename(url.split('?')[0])
            if not filename or '.' not in filename:
                raise ValueError("无法从URL提取有效文件名")
        except:
            # 生成随机文件名
            ext = '.png'  # 默认扩展名
            if content_type:
                # 根据内容类型设置扩展名
                ext_map = {
                    'image/jpeg': '.jpg',
                    'image/png': '.png',
                    'image/gif': '.gif',
                    'image/bmp': '.bmp',
                    'image/webp': '.webp'
                }
                ext = ext_map.get(content_type, '.png')
            
            filename = f"{uuid.uuid4().hex}{ext}"
        
        # 添加随机前缀避免冲突
        random_prefix = uuid.uuid4().hex[:8]
        filename = f"{random_prefix}_{filename}"
        filename = secure_filename(filename)
        
        # 保存文件
        file_path = os.path.join(upload_folder, filename)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # 验证下载的文件是否为有效图片
        try:
            with PILImage.open(file_path) as img:
                # 获取图片尺寸
                width, height = img.size
                current_app.logger.info(f"图片下载成功: {filename}, 尺寸: {width}x{height}")
        except Exception as img_error:
            current_app.logger.error(f"下载的文件不是有效图片: {str(img_error)}")
            # 删除无效文件
            os.remove(file_path)
            raise ValueError("下载的文件不是有效图片")
        
        # 返回本地URL
        local_url = f"/api/static/uploads/{subfolder}/{filename}"
        current_app.logger.info(f"图片下载完成，本地URL: {local_url}")
        return local_url
    
    except Exception as e:
        current_app.logger.error(f"下载图片失败: {str(e)}")
        # 如果下载失败，返回一个默认的错误图片
        return "/api/static/error-image.svg"