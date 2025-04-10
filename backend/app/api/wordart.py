r'''
 * @Author: JustSOOw wang813104@outlook.com
 * @Date: 2025-03-10 11:39:23
 * @LastEditors: JustSOOw wang813104@outlook.com
 * @LastEditTime: 2025-03-22 15:18:10
 * @FilePath: \WebArt\backend\app\api\wordart.py
 * @Description: 
 * @
 * @Copyright (c) 2025 by Furdow, All Rights Reserved. 
'''
from flask import Blueprint, request, jsonify, current_app, session
from flask_login import current_user, login_required
from app import db
from app.models import Image
from app.utils import DashScopeAPI, download_remote_image

wordart_bp = Blueprint('wordart', __name__)

@wordart_bp.route('/generate', methods=['POST'])
def generate():
    """
    提交百家姓生成任务
    """
    data = request.get_json()
    
    # 验证必要字段
    if not data or 'model' not in data or 'input' not in data:
        return jsonify({'error': '缺少必要字段'}), 400
    
    if 'surname' not in data['input']:
        return jsonify({'error': '缺少姓氏字段'}), 400
    
    # 验证姓氏长度
    surname = data['input']['surname']
    if not surname or len(surname) > 2:
        return jsonify({'error': '姓氏必须为1-2个汉字'}), 400
    
    # 获取API密钥
    api_key = current_app.config['DASHSCOPE_API_KEY']
    if not api_key:
        return jsonify({'error': 'API密钥未配置'}), 500
    
    try:
        # 调用DashScope API
        api = DashScopeAPI(api_key)
        response = api.generate_surname_art(data)
        
        # 记录任务信息
        style = data['input'].get('style', 'diy')
        style_name = get_style_display_name(style)
        
        # 保存任务信息到会话中，以便后续查询时使用
        task_id = response['output']['task_id']
        task_info = {
            'surname': surname,
            'style': style,
            'style_name': style_name,
            'prompt': data['input'].get('prompt'),
            'ref_image_url': data['input'].get('ref_image_url')
        }
        
        # 如果有字体设置
        if 'text' in data['input']:
            text_data = data['input']['text']
            task_info.update({
                'font_name': text_data.get('font_name'),
                'ttf_url': text_data.get('ttf_url'),
                'text_strength': text_data.get('text_strength'),
                'text_inverse': text_data.get('text_inverse')
            })
        
        # 保存任务信息到会话
        if 'task_info' not in session:
            session['task_info'] = {}
        session['task_info'][task_id] = task_info
        
        # 返回响应
        return jsonify(response)
    
    except Exception as e:
        current_app.logger.error(f"Error generating image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@wordart_bp.route('/tasks/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """
    获取任务状态
    """
    if not task_id:
        return jsonify({'error': '缺少任务ID'}), 400
    
    # 获取API密钥
    api_key = current_app.config['DASHSCOPE_API_KEY']
    if not api_key:
        return jsonify({'error': 'API密钥未配置'}), 500
    
    try:
        # 调用DashScope API
        api = DashScopeAPI(api_key)
        response = api.get_task_status(task_id)
        
        # 如果任务成功完成，保存图片信息到数据库
        if response['output']['task_status'] == 'SUCCEEDED' and 'results' in response['output']:
            # 获取任务信息
            task_info = None
            if 'task_info' in session and task_id in session['task_info']:
                task_info = session['task_info'][task_id]
                # 清除会话中的任务信息
                del session['task_info'][task_id]
                session.modified = True
            
            save_task_results(task_id, response['output']['results'], task_info)
        
        return jsonify(response)
    
    except Exception as e:
        current_app.logger.error(f"Error checking task status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@wordart_bp.route('/images', methods=['GET'])
def get_images():
    """
    获取图片列表
    """
    # 分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 查询条件
    query = Image.query
    
    # 如果用户已登录，只显示该用户的图片
    if current_user.is_authenticated:
        query = query.filter_by(user_id=current_user.id)
    
    # 按创建时间降序排序
    query = query.order_by(Image.created_at.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page)
    
    # 构建响应
    images = [image.to_dict() for image in pagination.items]
    
    return jsonify({
        'images': images,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@wordart_bp.route('/images/<int:image_id>', methods=['GET'])
def get_image(image_id):
    """
    获取单个图片详情
    """
    image = Image.query.get_or_404(image_id)
    
    # 如果用户已登录且不是该图片的所有者，返回403
    if current_user.is_authenticated and image.user_id and image.user_id != current_user.id:
        return jsonify({'error': '无权访问该图片'}), 403
    
    return jsonify(image.to_dict())

@wordart_bp.route('/images/save', methods=['POST'])
@login_required
def save_images():
    """
    保存用户生成的图片
    """
    data = request.get_json()
    
    if not data or 'images' not in data:
        return jsonify({'error': '缺少图片数据'}), 400
    
    images_data = data['images']
    if not isinstance(images_data, list):
        return jsonify({'error': '图片数据格式错误'}), 400
    
    saved_images = []
    new_images_to_add = []
    processed_urls = set() # 避免重复处理同一个远程URL
    
    try:
        for img_data in images_data:
            remote_url = img_data.get('url')
            task_id = img_data.get('task_id')

            if not remote_url or not task_id:
                 current_app.logger.warning(f"用户 {current_user.id} 尝试保存图片时跳过无效数据: {img_data}")
                 continue

            if remote_url in processed_urls:
                continue # 跳过已处理的URL
            processed_urls.add(remote_url)
            
            # 下载远程图片到本地服务器 (保存到 images 子文件夹)
            local_url_tuple = download_remote_image(remote_url, 'images')
            local_url = local_url_tuple[0]
            error_message = local_url_tuple[1]
            
            if local_url is None:
                current_app.logger.error(f"用户 {current_user.id} 保存图片失败: 无法下载或验证 {remote_url}。错误: {error_message}")
                continue # 跳过这个图片的保存
            
            # 检查图片是否已存在 (使用本地URL和任务ID)
            existing_image = Image.query.filter_by(
                task_id=task_id,
                url=local_url, # 使用本地URL检查
                user_id=current_user.id
            ).first()
            
            if existing_image:
                saved_images.append(existing_image.to_dict()) # 将已存在的图片加入返回列表
                continue # 跳过创建
            
            # 创建新图片记录
            image = Image(
                task_id=task_id,
                url=local_url, # 使用验证后的本地URL
                original_url=remote_url,
                surname=img_data.get('surname'),
                style=img_data.get('style'),
                style_name=img_data.get('style_name'),
                prompt=img_data.get('prompt'),
                ref_image_url=img_data.get('ref_image_url'),
                font_name=img_data.get('font_name'),
                ttf_url=img_data.get('ttf_url'),
                text_strength=img_data.get('text_strength'),
                text_inverse=img_data.get('text_inverse', False),
                user_id=current_user.id
            )
            
            new_images_to_add.append(image) # 收集新图片对象
        
        # 批量添加新图片并提交
        if new_images_to_add:
            db.session.add_all(new_images_to_add)
            db.session.commit()
            # 将新保存的图片添加到返回列表
            for img in new_images_to_add:
                 saved_images.append(img.to_dict())
        
        return jsonify({
            'message': f'成功处理 {len(images_data)} 个图片请求，保存/更新了 {len(saved_images)} 张图片记录',
            'images': saved_images
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"用户 {current_user.id} 保存图片时发生错误: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc()) # 记录完整的回溯信息
        return jsonify({'error': f'保存图片时发生服务器内部错误: {str(e)}'}), 500

def get_style_display_name(style_code):
    """
    获取风格的显示名称
    """
    style_map = {
        'fantasy_pavilion': '奇幻楼阁',
        'peerless_beauty': '绝色佳人',
        'landscape_pavilion': '山水楼阁',
        'traditional_buildings': '古风建筑',
        'green_dragon_girl': '青龙女侠',
        'cherry_blossoms': '樱花烂漫',
        'lovely_girl': '可爱少女',
        'ink_hero': '水墨少侠',
        'anime_girl': '动漫少女',
        'lake_pavilion': '水中楼阁',
        'tranquil_countryside': '宁静乡村',
        'dusk_splendor': '黄昏美景',
        'diy': '自定义风格'
    }
    
    return style_map.get(style_code, style_code)

def save_task_results(task_id, results, task_info=None):
    """
    保存任务结果到数据库 (由 get_task_status 调用)
    """
    # 获取任务相关信息
    if task_info is None:
        task_info = {}
    
    # 获取用户ID (如果用户已登录)
    user_id = current_user.id if current_user.is_authenticated else None
    
    images_to_add = [] # 收集需要添加的新图片
    
    # 保存每个图片
    for result in results:
        remote_url = result.get('url')
        if not remote_url:
            current_app.logger.warning(f"任务 {task_id} 的结果中缺少 URL: {result}")
            continue
        
        # 精确重复检查：检查是否已存在具有相同 task_id 和 original_url 的记录
        existing_image = Image.query.filter_by(
            task_id=task_id,
            original_url=remote_url,
            # 如果需要区分用户，可以加上 user_id (取决于业务逻辑)
            # user_id=user_id 
        ).first()

        if existing_image:
            current_app.logger.info(f"任务 {task_id} 的图片 {remote_url} 已存在，跳过保存。")
            continue # 如果已存在，跳过此图片

        # 下载远程图片到本地服务器 (保存到 images 子文件夹)
        local_url_tuple = download_remote_image(remote_url, 'images')
        
        # 检查下载是否成功
        local_url = local_url_tuple[0]
        error_message = local_url_tuple[1]
        
        if local_url is None:
            current_app.logger.error(f"保存任务 {task_id} 的图片失败: 无法下载或验证 {remote_url}。错误: {error_message}")
            continue # 跳过这个图片的保存

        image = Image(
            task_id=task_id,
            url=local_url, # 使用解包后的 URL
            original_url=remote_url,  # 保存原始URL以备参考
            surname=task_info.get('surname', ''),
            style=task_info.get('style', ''),
            style_name=get_style_display_name(task_info.get('style', '')),
            prompt=task_info.get('prompt'),
            ref_image_url=task_info.get('ref_image_url'),
            font_name=task_info.get('font_name'),
            ttf_url=task_info.get('ttf_url'),
            text_strength=task_info.get('text_strength'),
            text_inverse=task_info.get('text_inverse', False),
            user_id=user_id
        )
        images_to_add.append(image)
    
    # 批量添加新图片
    if images_to_add:
        try:
            db.session.add_all(images_to_add)
            db.session.commit()
            current_app.logger.info(f"为任务 {task_id} 成功保存了 {len(images_to_add)} 张新图片。")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"为任务 {task_id} 批量保存图片时出错: {str(e)}") 