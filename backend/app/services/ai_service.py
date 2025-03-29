'''
Author: JustSOOw wang813104@outlook.com
Date: 2025-03-20 11:00:00
LastEditors: AI Assistant
LastEditTime: 2025-03-20 11:00:00
FilePath: /WebArt/backend/app/services/ai_service.py
Description: AI模型调用服务

Copyright (c) 2025 by Furdow, All Rights Reserved. 
'''
import os
import json
import base64
import requests
from typing import List, Dict, Any, Optional, Generator
from flask import current_app

class AIService:
    """AI服务类，处理与大模型API的交互"""
    
    def __init__(self):
        """初始化AI服务"""
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        if not self.api_key:
            raise ValueError("未设置DASHSCOPE_API_KEY环境变量")
            
        # 百炼平台兼容OpenAI接口的基础URL
        self.compatible_base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        # 原生DashScope API的基础URL
        self.dashscope_base_url = "https://dashscope.aliyuncs.com/api/v1"
        
        # 支持的模型配置
        self.models = {
            "qwen-turbo": {
                "api_type": "compatible",  # 使用OpenAI兼容接口
                "model_id": "qwen-turbo",
                "capabilities": ["text"]
            },
            "qwen-plus": {
                "api_type": "compatible",  # 使用OpenAI兼容接口
                "model_id": "qwen-plus",
                "capabilities": ["text"]
            },
            "qwen-max-latest": {
                "api_type": "compatible",  # 使用OpenAI兼容接口
                "model_id": "qwen-max-latest",
                "capabilities": ["text"]
            },
            "qwen-omni-turbo": {
                "api_type": "compatible",  # 使用OpenAI兼容接口
                "model_id": "qwen-omni-turbo",
                "capabilities": ["text", "image", "audio", "video"]
            }
        }
    
    def get_headers(self, api_type: str = "compatible") -> Dict[str, str]:
        """获取API请求头
        
        Args:
            api_type: API类型，可选值为 'compatible'(OpenAI兼容) 或 'dashscope'(原生DashScope)
            
        Returns:
            HTTP请求头字典
        """
        if api_type == "compatible":
            return {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        elif api_type == "dashscope":
            return {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        else:
            raise ValueError(f"不支持的API类型: {api_type}")
    
    def text_completion(self, 
                       messages: List[Dict[str, Any]], 
                       model: str = "qwen-max-latest",
                       stream: bool = False,
                       temperature: float = 0.7,
                       max_tokens: int = None) -> Dict[str, Any]:
        """处理文本聊天请求
        
        Args:
            messages: 聊天历史消息列表
            model: 使用的模型ID
            stream: 是否使用流式输出
            temperature: 温度参数，控制随机性
            max_tokens: 最大生成token数
            
        Returns:
            API返回的响应对象
        """
        if model not in self.models:
            raise ValueError(f"不支持的模型: {model}")
        
        model_config = self.models[model]
        base_url = self.compatible_base_url
        
        # 构建请求数据
        request_data = {
            "model": model_config["model_id"],
            "messages": messages,
            "stream": stream,
            "temperature": temperature,
        }
        
        # 只有在指定时添加max_tokens参数
        if max_tokens is not None:
            request_data["max_tokens"] = max_tokens
        
        try:
            # 发送API请求
            response = requests.post(
                f"{base_url}/chat/completions",
                headers=self.get_headers(model_config["api_type"]),
                json=request_data
            )
            
            # 检查响应
            if response.status_code != 200:
                error_detail = response.json() if response.text else {"error": "未知错误"}
                current_app.logger.error(f"AI API调用失败: {response.status_code}, {error_detail}")
                return {
                    "error": True,
                    "status_code": response.status_code,
                    "message": f"API调用失败: {error_detail}"
                }
                
            return response.json()
            
        except Exception as e:
            current_app.logger.error(f"AI API调用异常: {str(e)}")
            return {
                "error": True,
                "message": f"API请求异常: {str(e)}"
            }
    
    def stream_text_completion(self, 
                              messages: List[Dict[str, Any]], 
                              model: str = "qwen-max-latest",
                              temperature: float = 0.7,
                              max_tokens: int = None) -> Generator[Dict[str, Any], None, None]:
        """流式处理文本聊天请求
        
        Args:
            messages: 聊天历史消息列表
            model: 使用的模型ID
            temperature: 温度参数，控制随机性
            max_tokens: 最大生成token数
            
        Yields:
            API流式响应的每个数据块
        """
        if model not in self.models:
            raise ValueError(f"不支持的模型: {model}")
        
        model_config = self.models[model]
        base_url = self.compatible_base_url
        
        # 构建请求数据
        request_data = {
            "model": model_config["model_id"],
            "messages": messages,
            "stream": True,
            "temperature": temperature,
            "stream_options": {"include_usage": True},
            "modalities": ["text"]  # 明确指定输出模态为文本
        }
        
        # 只有在指定时添加max_tokens参数
        if max_tokens is not None:
            request_data["max_tokens"] = max_tokens
        
        try:
            # 发送API请求
            response = requests.post(
                f"{base_url}/chat/completions",
                headers=self.get_headers(model_config["api_type"]),
                json=request_data,
                stream=True
            )
            
            # 检查初始响应
            if response.status_code != 200:
                error_detail = response.json() if response.text else {"error": "未知错误"}
                current_app.logger.error(f"AI API流式调用失败: {response.status_code}, {error_detail}")
                yield {
                    "error": True,
                    "status_code": response.status_code,
                    "message": f"API调用失败: {error_detail}"
                }
                return
                
            # 处理流式响应
            for line in response.iter_lines():
                if line:
                    if line.strip() == b'data: [DONE]':
                        break
                    
                    if line.startswith(b'data: '):
                        json_data = json.loads(line[6:])
                        yield json_data
            
        except Exception as e:
            current_app.logger.error(f"AI API流式调用异常: {str(e)}")
            yield {
                "error": True,
                "message": f"API流式请求异常: {str(e)}"
            }
    
    def multimodal_completion(self, 
                             messages: List[Dict[str, Any]], 
                             model: str = "qwen-omni-turbo",
                             stream: bool = True,
                             temperature: float = 0.7,
                             max_tokens: int = None) -> Generator[Dict[str, Any], None, None]:
        """处理多模态聊天请求，支持图像、音频、视频输入
        
        Args:
            messages: 聊天历史消息列表，包含多模态内容
            model: 使用的模型ID
            stream: 是否使用流式输出 (Omni模型必须使用流式输出)
            temperature: 温度参数，控制随机性
            max_tokens: 最大生成token数
            
        Returns:
            API返回的响应对象，如果stream=True则是生成器
        """
        if model not in self.models or "image" not in self.models[model]["capabilities"]:
            raise ValueError(f"模型 {model} 不支持多模态输入")
        
        # Omni模型只支持流式输出
        if model == "qwen-omni-turbo" and not stream:
            current_app.logger.warning("Qwen-Omni模型只支持流式输出，已自动启用流式模式")
            stream = True
        
        model_config = self.models[model]
        base_url = self.compatible_base_url
        
        # 记录传入的消息格式
        current_app.logger.info(f"多模态调用 - 消息数量: {len(messages)}")
        
        # 构建请求数据 - 按照Omni官方文档格式
        request_data = {
            "model": model_config["model_id"],
            "messages": messages,
            # 设置输出数据的模态，当前仅支持["text"]
            "modalities": ["text"],
            # stream 必须设置为 True，否则会报错
            "stream": True,
            "temperature": temperature,
            "stream_options": {"include_usage": True}
        }
        
        # 只有在指定时添加max_tokens参数
        if max_tokens is not None:
            request_data["max_tokens"] = max_tokens
        
        try:
            current_app.logger.info(f"发送多模态请求到: {base_url}/chat/completions")
            current_app.logger.debug(f"请求体: {json.dumps(request_data)}")
            
            # 发送API请求
            response = requests.post(
                f"{base_url}/chat/completions",
                headers=self.get_headers(model_config["api_type"]),
                json=request_data,
                stream=True,
                timeout=120  # 设置120秒超时
            )
            
            # 检查初始响应
            if response.status_code != 200:
                error_text = response.text
                try:
                    error_detail = response.json() if error_text else {"error": "未知错误"}
                except:
                    error_detail = {"error": "无法解析错误响应", "text": error_text[:200]}
                    
                current_app.logger.error(f"多模态API调用失败: {response.status_code}, {error_detail}")
                yield {
                    "error": True,
                    "status_code": response.status_code,
                    "message": f"API调用失败: {error_detail}"
                }
                return
            
            current_app.logger.info(f"多模态API调用成功，开始处理流式响应")
                
            # 处理流式响应
            for line in response.iter_lines():
                if line:
                    current_app.logger.debug(f"收到行: {line}")
                    if line.strip() == b'data: [DONE]':
                        break
                    
                    if line.startswith(b'data: '):
                        try:
                            json_data = json.loads(line[6:])
                            yield json_data
                        except json.JSONDecodeError as e:
                            current_app.logger.error(f"JSON解析错误: {str(e)}, 行: {line}")
                            yield {
                                "error": True,
                                "message": f"JSON解析错误: {str(e)}"
                            }
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"HTTP请求异常: {str(e)}")
            yield {
                "error": True,
                "message": f"HTTP请求异常: {str(e)}"
            }
        except Exception as e:
            current_app.logger.error(f"多模态API调用异常: {str(e)}")
            yield {
                "error": True,
                "message": f"API请求异常: {str(e)}"
            }
    
    def encode_image(self, image_path: str) -> str:
        """将本地图片编码为base64字符串
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            base64编码的图片字符串
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
            
    def get_image_content(self, image_url: str, is_local: bool = False) -> Dict[str, Any]:
        """生成图片内容格式
        
        Args:
            image_url: 图片URL或本地路径
            is_local: 是否为本地文件
            
        Returns:
            格式化的图片内容对象
        """
        if is_local:
            base64_image = self.encode_image(image_url)
            return {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }
        else:
            # 如果是相对路径，转换为完整URL
            if image_url.startswith('/'):
                # 这里可以根据实际部署环境调整URL
                server_url = current_app.config.get('SERVER_URL', 'http://localhost:5000')
                image_url = f"{server_url}{image_url}"
                
            return {
                "type": "image_url",
                "image_url": {
                    "url": image_url
                }
            }
    
    def get_audio_content(self, audio_url: str, audio_format: str = "mp3") -> Dict[str, Any]:
        """生成音频内容格式
        
        Args:
            audio_url: 音频URL
            audio_format: 音频格式 (mp3,wav,m4a等)
            
        Returns:
            格式化的音频内容对象
        """
        # 如果是相对路径，转换为完整URL
        if audio_url.startswith('/'):
            server_url = current_app.config.get('SERVER_URL', 'http://localhost:5000')
            audio_url = f"{server_url}{audio_url}"
            
        return {
            "type": "input_audio",
            "input_audio": {
                "data": audio_url,
                "format": audio_format
            }
        }
    
    def get_video_content(self, video_url: str, as_frames: bool = False, frames: List[str] = None) -> Dict[str, Any]:
        """生成视频内容格式
        
        Args:
            video_url: 视频URL
            as_frames: 是否以帧序列形式传入
            frames: 帧图像URL列表
            
        Returns:
            格式化的视频内容对象
        """
        # 如果是相对路径，转换为完整URL
        if video_url and video_url.startswith('/'):
            server_url = current_app.config.get('SERVER_URL', 'http://localhost:5000')
            video_url = f"{server_url}{video_url}"
        
        # 两种视频输入方式：视频文件 或 帧序列
        if as_frames and frames:
            # 帧序列方式 (至少4张，最多80张)
            if len(frames) < 4:
                current_app.logger.warning("视频帧数量少于4张，可能导致识别效果不佳")
            
            # 确保所有帧都是完整URL
            full_frames = []
            for frame in frames:
                if frame.startswith('/'):
                    server_url = current_app.config.get('SERVER_URL', 'http://localhost:5000')
                    full_frames.append(f"{server_url}{frame}")
                else:
                    full_frames.append(frame)
                    
            return {
                "type": "video",
                "video": full_frames
            }
        else:
            # 视频文件方式
            return {
                "type": "video_url",
                "video_url": {
                    "url": video_url
                }
            }
    
    def format_multimodal_message(self, role: str, text: str, media: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """格式化多模态消息
        
        Args:
            role: 消息角色 ('user', 'assistant', 'system')
            text: 文本内容
            media: 媒体内容对象 (图像、音频、视频)
            
        Returns:
            格式化的消息对象
        """
        # 单一模态消息可以直接使用text字段
        if media is None:
            return {
                "role": role,
                "content": text
            }
        
        # 构建多模态消息内容
        content = []
        
        # 添加媒体内容 - Omni模型要求在前面放媒体，后面放文本
        content.append(media)
        
        # 添加文本内容
        content.append({
            "type": "text",
            "text": text
        })
        
        return {
            "role": role,
            "content": content
        } 