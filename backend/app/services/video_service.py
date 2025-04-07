'''
Author: JustSOOw wang813104@outlook.com
Date: 2025-04-03 14:40:00
LastEditors: AI Assistant
LastEditTime: 2025-04-04 10:30:00
FilePath: /WebArt/backend/app/services/video_service.py
Description: 视频生成服务，封装与DashScope API的交互

Copyright (c) 2025 by Furdow, All Rights Reserved. 
'''
import os
import time
import requests
import json
from flask import current_app, request
from app import db
from app.models import Video
from app.utils.file_utils import save_uploaded_file, download_remote_file, allowed_video_file
from datetime import datetime

# 尝试导入DashScope SDK
try:
    from http import HTTPStatus
    from dashscope import VideoSynthesis # type: ignore
    DASHSCOPE_SDK_AVAILABLE = True
except ImportError:
    DASHSCOPE_SDK_AVAILABLE = False

class VideoService:
    """视频生成服务，封装与DashScope API的交互"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or current_app.config['DASHSCOPE_API_KEY']
        self.base_url = 'https://dashscope.aliyuncs.com/api/v1'
        self.headers = {
            'X-DashScope-Async': 'enable',
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        # 如果SDK可用，则配置环境变量
        if DASHSCOPE_SDK_AVAILABLE:
            os.environ['DASHSCOPE_API_KEY'] = self.api_key
            current_app.logger.info("DashScope SDK可用，将使用SDK方式调用API")
        else:
            current_app.logger.warning("DashScope SDK不可用，将使用HTTP方式调用API")
    
    def create_text_to_video_task(self, data, user_id=None):
        """
        创建文生视频任务
        
        Args:
            data (dict): 前端传递的数据
            user_id (int, optional): 用户ID
            
        Returns:
            tuple: (Video对象, 错误信息)
        """
        try:
            # 提取参数
            model = data.get('model')
            prompt = data.get('prompt')
            size = data.get('size')
            seed = data.get('seed')
            prompt_extend = data.get('prompt_extend', True)
            
            if not model or not prompt:
                return None, "缺少必要参数"
            
            # 创建视频记录
            video = Video(
                prompt=prompt,
                model=model,
                type="text-to-video",
                size=size,
                seed=seed,
                prompt_extend=prompt_extend,
                status="PENDING",
                user_id=user_id
            )
            
            # 构建SDK参数字典
            sdk_params = {
                "model": model,
                "prompt": prompt,
            }
            
            if size:
                sdk_params["size"] = size
                
            if seed:
                sdk_params["seed"] = seed
                
            if prompt_extend is not None:
                sdk_params["prompt_extend"] = prompt_extend
            
            # 构建HTTP请求参数
            http_payload = {
                "model": model,
                "input": {
                    "prompt": prompt
                },
                "parameters": {
                    "prompt_extend": prompt_extend
                }
            }
            
            if size:
                http_payload["parameters"]["size"] = size
                
            if seed:
                http_payload["parameters"]["seed"] = seed
            
            # 提交任务 - 始终使用异步HTTP提交，立即获取task_id
            response = self._submit_task(http_payload)
                
            task_id = response['output']['task_id']
            
            # 更新视频记录
            video.task_id = task_id
            db.session.add(video)
            db.session.commit()
            
            return video, None
            
        except Exception as e:
            current_app.logger.error(f"创建文生视频任务失败: {str(e)}")
            return None, str(e)
    
    def create_image_to_video_task(self, data, image_file=None, user_id=None):
        """
        创建图生视频任务
        
        Args:
            data (dict): 前端传递的数据
            image_file (FileStorage, optional): 上传的图片文件
            user_id (int, optional): 用户ID
            
        Returns:
            tuple: (Video对象, 错误信息)
        """
        try:
            # 提取参数
            model = data.get('model')
            prompt = data.get('prompt')
            resolution = data.get('resolution')
            duration = data.get('duration')
            seed = data.get('seed')
            prompt_extend = data.get('prompt_extend', True)
            img_url = data.get('img_url')
            
            if not model or not prompt or (not img_url and not image_file):
                return None, "缺少必要参数"
            
            # 处理上传图片
            source_image = None
            if image_file:
                # 保存上传的图片
                # 注意：upload_folder 是绝对路径
                upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'video_sources')
                os.makedirs(upload_folder, exist_ok=True)
                
                filename = save_uploaded_file(image_file, upload_folder)
                if not filename:
                    return None, "图片保存失败"
                
                # 构建供AI访问的img_url
                public_base_url = current_app.config.get('PUBLIC_BASE_URL')
                # 使用正确的路径，不包含项目名称
                relative_path_for_url = f"static/uploads/video_sources/{os.path.basename(filename)}"
                
                if public_base_url:
                    # 使用配置的公开基础URL
                    img_url = f"{public_base_url.rstrip('/')}/{relative_path_for_url}"
                    current_app.logger.info(f"使用公开访问URL (ngrok/other): {img_url}")
                else:
                    # 回退到旧逻辑 (可能无法从外部访问)
                    current_app.logger.warning("PUBLIC_BASE_URL 未在 .env 中配置，回退到本地服务器URL。这可能导致外部AI服务无法访问图片。")
                    # 尝试从请求或配置获取主机名和端口，更健壮的回退
                    host = request.host.split(':')[0]
                    port = current_app.config.get('SERVER_PORT', '5000') # 假设后端运行在5000端口，如果配置了SERVER_PORT则使用
                    scheme = request.scheme
                    server_name = f"{host}:{port}" if port else host
                    img_url = f"{scheme}://{server_name}/{relative_path_for_url}"
                    current_app.logger.warning(f"回退使用的本地URL: {img_url}")

                # 数据库中存储本地相对路径，供内部使用
                source_image = os.path.join('video_sources', os.path.basename(filename)).replace('\\', '/') # 保证斜杠统一
            
            elif data.get('image_url'):
                # 如果直接提供了外部URL
                img_url = data.get('image_url')
                source_image = None # 没有本地源文件
                current_app.logger.info(f"使用请求中提供的外部图片URL: {img_url}")
            else:
                # 既没有文件也没有URL，这在API层应该已经被阻止了
                return None, "无效的图片输入"

            # 创建视频记录
            video = Video(
                prompt=prompt,
                model=model,
                type="image-to-video",
                source_image=source_image,
                resolution=resolution,
                duration=duration,
                seed=seed,
                prompt_extend=prompt_extend,
                status="PENDING",
                user_id=user_id
            )
            
            # 构建SDK参数字典
            sdk_params = {
                "model": model,
                "prompt": prompt,
                "img_url": img_url
            }
            
            if resolution:
                sdk_params["resolution"] = resolution
                
            if duration and model == "wanx2.1-i2v-turbo":  # 只有turbo模型支持调整时长
                sdk_params["duration"] = duration
                
            if seed:
                sdk_params["seed"] = seed
                
            if prompt_extend is not None:
                sdk_params["prompt_extend"] = prompt_extend
            
            # 构建HTTP请求参数
            http_payload = {
                "model": model,
                "input": {
                    "prompt": prompt,
                    "img_url": img_url
                },
                "parameters": {
                    "prompt_extend": prompt_extend
                }
            }
            
            if resolution:
                http_payload["parameters"]["resolution"] = resolution
                
            if duration and model == "wanx2.1-i2v-turbo":  # 只有turbo模型支持调整时长
                http_payload["parameters"]["duration"] = duration
                
            if seed:
                http_payload["parameters"]["seed"] = seed
            
            # 提交任务 - 始终使用异步HTTP提交，立即获取task_id
            response = self._submit_task(http_payload)
                
            task_id = response['output']['task_id']
            
            # 更新视频记录
            video.task_id = task_id
            db.session.add(video)
            db.session.commit()
            
            return video, None
            
        except Exception as e:
            current_app.logger.error(f"创建图生视频任务失败: {str(e)}")
            return None, str(e)
    
    def check_task_status(self, task_id):
        """Checks task status using SDK if available, otherwise HTTP."""
        if not self.api_key:
            raise ValueError("API Key is required")

        result = None
        try:
            current_app.logger.info(f"检查任务状态 for task_id: {task_id}, SDK available: {DASHSCOPE_SDK_AVAILABLE}")
            if DASHSCOPE_SDK_AVAILABLE:
                response = VideoSynthesis.fetch(task_id)
                current_app.logger.debug(f"SDK fetch response for {task_id}: Status={response.status_code}, Code={response.code}, Msg={response.message}")
                if response.status_code == HTTPStatus.OK:
                    # 直接使用 response 对象，它行为类似字典
                    result = response 
                # Handle specific case where task might not be found yet (example error code)
                # Note: Adjust 'TaskNotFound' if DashScope uses a different code
                elif response.code == 'TaskNotFound':
                     current_app.logger.warning(f"任务 {task_id} 尚未找到 (SDK)，可能正在创建中。")
                     # Return a temporary status to indicate polling should continue
                     return {'output': {'task_status': 'PENDING', 'task_id': task_id}, 'message': 'Task pending or not found yet'}
                else:
                    # Raise for other SDK errors
                    raise Exception(f"SDK任务查询失败: Code={response.code}, Message={response.message}")
            else:
                url = f"{self.base_url}/tasks/{task_id}"
                response = requests.get(url, headers={'Authorization': f'Bearer {self.api_key}'})
                current_app.logger.debug(f"HTTP GET response for {task_id}: Status={response.status_code}, Body={response.text[:200]}") # Log partial body
                # Check specifically for 404 Not Found
                if response.status_code == 404:
                     current_app.logger.warning(f"任务 {task_id} 尚未找到 (HTTP 404)，可能正在创建中。")
                     return {'output': {'task_status': 'PENDING', 'task_id': task_id}, 'message': 'Task pending or not found yet'}
                # Raise for other HTTP errors (4xx, 5xx)
                response.raise_for_status()
                result = response.json()

            if not result or 'output' not in result or 'task_status' not in result['output']:
                 current_app.logger.error(f"从DashScope收到的任务结果格式无效 for {task_id}: {result}")
                 raise ValueError("无效的任务结果格式")

            current_app.logger.info(f"任务 {task_id} 状态: {result['output']['task_status']}")

            # --- Update DB ---
            video = Video.query.filter_by(task_id=task_id).first()
            if video:
                task_status = result['output']['task_status']
                # Only update if status changed to avoid unnecessary commits
                if video.status != task_status:
                    video.status = task_status
                    current_app.logger.info(f"更新任务 {task_id} 数据库状态为: {task_status}")

                    if task_status == 'SUCCEEDED' and 'video_url' in result['output']:
                        video_url = result['output']['video_url']
                        video.video_url = video_url
                        current_app.logger.info(f"任务 {task_id} 成功，视频URL: {video_url}")
                        # Trigger download in a background task if needed, or handle here
                        try:
                            video_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'videos')
                            os.makedirs(video_folder, exist_ok=True)
                            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                            # Use a secure filename approach or ensure the task_id/video.id is safe for filenames
                            filename = f"video_{video.id}_{timestamp}.mp4"
                            local_path = os.path.join(video_folder, filename)
                            current_app.logger.info(f"开始下载视频 for {task_id} from {video_url} to {local_path}")
                            success = download_remote_file(video_url, local_path)
                            if success:
                                # Store relative path from the base upload folder
                                relative_path = os.path.relpath(local_path, current_app.config['UPLOAD_FOLDER'])
                                video.local_path = relative_path.replace('\\\\', '/') # Ensure forward slashes for web paths
                                current_app.logger.info(f"视频 {task_id} 下载成功到: {video.local_path}")
                            else:
                                 current_app.logger.error(f"视频 {task_id} 下载失败 from {video_url}")
                                 # Optionally set an error message or status here
                        except Exception as download_e:
                            current_app.logger.error(f"下载视频时出错 for task {task_id}: {str(download_e)}", exc_info=True)
                            # Optionally set an error message or status here

                    elif task_status == 'FAILED':
                        error_message = result['output'].get('message', '任务执行失败')
                        video.error_message = error_message
                        current_app.logger.warning(f"任务 {task_id} 失败: {error_message}")

                    try:
                        db.session.commit()
                    except Exception as db_e:
                        current_app.logger.error(f"提交数据库更改时出错 for task {task_id}: {str(db_e)}", exc_info=True)
                        db.session.rollback() # Rollback on error
                        raise # Re-raise DB error
                else:
                     current_app.logger.debug(f"任务 {task_id} 状态未改变 ({video.status})，无需更新数据库。")

            else:
                 current_app.logger.warning(f"检查任务状态时未在数据库中找到任务 {task_id}")


            return result

        except requests.exceptions.RequestException as http_e:
            # Handle HTTP specific errors (network, timeout, etc.)
            current_app.logger.error(f"检查任务状态时HTTP请求失败 for task {task_id}: {str(http_e)}", exc_info=True)
            # Return a temporary error structure or re-raise depending on desired frontend handling
            # For now, re-raise to let the API handler return 500
            raise
        except ValueError as ve: # Catch specific errors like invalid format
             current_app.logger.error(f"检查任务状态时值错误 for task {task_id}: {str(ve)}", exc_info=True)
             raise
        except Exception as e:
            # Handle other errors (SDK, parsing, DB, etc.)
            current_app.logger.error(f"检查任务状态时发生意外错误 for task {task_id}: {str(e)}", exc_info=True)
            raise # Re-raise to be caught by API route
    
    def get_user_videos(self, user_id, page=1, per_page=10):
        """
        获取用户的视频列表
        
        Args:
            user_id (int): 用户ID
            page (int): 页码
            per_page (int): 每页数量
            
        Returns:
            tuple: (视频列表, 总数, 总页数)
        """
        current_app.logger.info(f"开始查询用户 {user_id} 的视频列表")
        query = Video.query.filter_by(user_id=user_id).order_by(Video.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page)
        
        current_app.logger.info(f"查询结果: 总数={pagination.total}, 当前页={page}, 总页数={pagination.pages}")
        current_app.logger.info(f"当前页视频数量: {len(pagination.items)}")
        
        videos = [video.to_dict() for video in pagination.items]
        current_app.logger.info(f"转换后的视频列表: {videos}")
        
        return videos, pagination.total, pagination.pages
    
    def _submit_task_sdk(self, params, task_type="text-to-video"):
        """
        使用SDK提交任务到DashScope
        
        Args:
            params (dict): SDK参数
            task_type (str): 任务类型，text-to-video或image-to-video
            
        Returns:
            dict: API响应
        """
        if not DASHSCOPE_SDK_AVAILABLE:
            raise ValueError("DashScope SDK不可用")
        
        try:
            current_app.logger.info(f"使用SDK提交{task_type}任务")
            
            # 同步调用SDK，会自动轮询任务直到完成
            if task_type == "text-to-video":
                response = VideoSynthesis.call(**params)
            else:  # image-to-video
                response = VideoSynthesis.call(**params)
                
            if response.status_code != HTTPStatus.OK:
                raise Exception(f"任务提交失败: {response.code} - {response.message}")
                
            # 将SDK响应转换为字典
            return response.to_dict()
            
        except Exception as e:
            current_app.logger.error(f"使用SDK提交任务失败: {str(e)}")
            raise
    
    def _submit_task(self, payload):
        """
        使用HTTP提交任务到DashScope
        
        Args:
            payload (dict): 请求参数
            
        Returns:
            dict: API响应
        """
        if not self.api_key:
            raise ValueError("API Key is required")
        
        url = f"{self.base_url}/services/aigc/video-generation/video-synthesis"
        
        try:
            current_app.logger.info("使用HTTP方式提交任务")
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"提交任务失败: {str(e)}")
            if hasattr(e, 'response') and e.response:
                current_app.logger.error(f"Response: {e.response.text}")
            raise 