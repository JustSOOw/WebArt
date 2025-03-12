import os
import uuid
import requests
from flask import current_app
from werkzeug.utils import secure_filename
from PIL import Image as PILImage

def allowed_image_file(filename):
    """
    检查图片文件扩展名是否允许
    """
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_font_file(filename):
    """
    检查字体文件扩展名是否允许
    """
    ALLOWED_EXTENSIONS = {'ttf'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, folder):
    """
    保存上传的文件
    
    Args:
        file: 上传的文件对象
        folder: 保存的文件夹名称 ('images' 或 'fonts')
        
    Returns:
        str: 文件的URL路径
    """
    filename = secure_filename(file.filename)
    # 生成唯一文件名
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    
    # 确保目录存在
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(upload_folder, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)
    
    # 返回文件URL
    return f"/api/static/uploads/{folder}/{unique_filename}"

def download_remote_image(url, folder='images'):
    """
    下载远程图片并保存到本地
    
    Args:
        url: 远程图片URL
        folder: 保存的文件夹名称
        
    Returns:
        str: 本地文件的URL路径
    """
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        # 从URL中提取文件名
        filename = url.split('/')[-1]
        if '?' in filename:
            filename = filename.split('?')[0]
        
        # 确保文件名安全
        filename = secure_filename(filename)
        if not filename:
            filename = f"{uuid.uuid4().hex}.jpg"
        
        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # 确保目录存在
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(upload_folder, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_folder, unique_filename)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # 返回文件URL
        return f"/api/static/uploads/{folder}/{unique_filename}"
    except Exception as e:
        current_app.logger.error(f"Error downloading image: {str(e)}")
        return None

def validate_image(file_path):
    """
    验证图片文件
    
    Args:
        file_path: 图片文件路径
        
    Returns:
        tuple: (是否有效, 宽, 高)
    """
    try:
        with PILImage.open(file_path) as img:
            width, height = img.size
            
            # 检查宽高比
            aspect_ratio = max(width, height) / min(width, height)
            if aspect_ratio > 2:
                return False, width, height, "宽高比不能超过2:1"
            
            # 检查最大边长
            max_dimension = max(width, height)
            if max_dimension > 2048:
                return False, width, height, "图像的长边不能超过2048像素"
            
            return True, width, height, None
    except Exception as e:
        current_app.logger.error(f"Error validating image: {str(e)}")
        return False, 0, 0, str(e) 