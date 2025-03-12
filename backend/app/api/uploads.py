import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from app.utils import allowed_image_file, allowed_font_file, save_uploaded_file, validate_image

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
            os.remove(file_path)
            return jsonify({'error': error_msg}), 400
        
        return jsonify({
            'url': file_url,
            'width': width,
            'height': height
        })
    
    except Exception as e:
        current_app.logger.error(f"Error uploading image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@uploads_bp.route('/upload-ttf', methods=['POST'])
def upload_font():
    """
    上传TTF字体文件
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
        return jsonify({'error': '不支持的文件类型，请上传ttf格式的字体文件'}), 400
    
    try:
        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > 30 * 1024 * 1024:  # 30MB
            return jsonify({'error': '字体文件大小不能超过30MB'}), 400
        
        # 保存文件
        file_url = save_uploaded_file(file, 'fonts')
        
        return jsonify({
            'url': file_url
        })
    
    except Exception as e:
        current_app.logger.error(f"Error uploading font: {str(e)}")
        return jsonify({'error': str(e)}), 500

@uploads_bp.route('/static/uploads/<path:filename>', methods=['GET'])
def serve_uploads(filename):
    """
    提供上传文件的访问
    """
    upload_folder = os.path.join(current_app.root_path, 'static/uploads')
    return send_from_directory(upload_folder, filename) 