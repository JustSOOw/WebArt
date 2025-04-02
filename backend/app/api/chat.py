'''
Author: JustSOOw wang813104@outlook.com
Date: 2025-03-20 11:30:00
LastEditors: AI Assistant
LastEditTime: 2025-03-22 12:00:00
FilePath: /WebArt/backend/app/api/chat.py
Description: 聊天API路由

Copyright (c) 2025 by Furdow, All Rights Reserved. 
'''
import os
import json
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, Response, current_app, stream_with_context, send_from_directory
from flask_login import login_required, current_user
from app import db
from app.models.chat import Conversation, Message
from app.services.ai_service import AIService
from werkzeug.utils import secure_filename

# 创建蓝图
chat_bp = Blueprint('chat', __name__)

# 初始化AI服务
ai_service = AIService()

# 可用模型列表
AVAILABLE_MODELS = [
    {
        "id": "qwen-turbo",
        "name": "通义千问-Turbo",
        "capabilities": ["text"]
    },
    {
        "id": "qwen-plus",
        "name": "通义千问-Plus",
        "capabilities": ["text"]
    },
    {
        "id": "qwen-max-latest",
        "name": "通义千问-Max",
        "capabilities": ["text"]
    },
    {
        "id": "qwen-omni-turbo",
        "name": "通义千问-Omni",
        "capabilities": ["text", "image", "audio", "video"]
    }
]

# 添加文件上传配置
UPLOAD_FOLDER = 'backend/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx', 'txt', 'mp3', 'wav', 'm4a', 'mp4', 'mov', 'avi'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@chat_bp.route('/models', methods=['GET'])
def get_models():
    """获取可用的AI模型列表"""
    return jsonify({
        "models": AVAILABLE_MODELS
    }), 200

@chat_bp.route('/conversations', methods=['GET'])
@login_required
def get_conversations():
    """获取当前用户的所有对话列表"""
    try:
        # 获取该用户的所有对话
        conversations = Conversation.query.filter_by(user_id=current_user.id).order_by(Conversation.updated_at.desc()).all()
        
        # 处理对话数据
        result = []
        for conversation in conversations:
            # 获取该对话的最后一条消息作为预览
            latest_message = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.created_at.desc()).first()
            preview = latest_message.content[:50] + "..." if latest_message and len(latest_message.content) > 50 else ""
            
            result.append({
                **conversation.to_dict(),
                "preview": preview
            })
        
        return jsonify({
            "conversations": result
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取对话列表失败: {str(e)}")
        return jsonify({
            "error": True,
            "message": "获取对话列表失败"
        }), 500

@chat_bp.route('/conversations', methods=['POST'])
@login_required
def create_conversation():
    """创建新的对话"""
    try:
        data = request.get_json()
        
        # 验证请求数据
        if not data:
            return jsonify({
                "error": True,
                "message": "无效的请求数据"
            }), 400
        
        # 获取标题和模型，设置默认值
        title = data.get('title', '新对话')
        model = data.get('model', 'qwen-max-latest')
        
        # 验证模型是否支持
        if model not in [m["id"] for m in AVAILABLE_MODELS]:
            return jsonify({
                "error": True,
                "message": f"不支持的模型: {model}"
            }), 400
        
        # 创建新对话
        conversation = Conversation(
            title=title,
            model=model,
            user_id=current_user.id
        )
        
        db.session.add(conversation)
        db.session.commit()
        
        return jsonify({
            "conversation": conversation.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建对话失败: {str(e)}")
        return jsonify({
            "error": True,
            "message": "创建对话失败"
        }), 500

@chat_bp.route('/conversations/<int:conversation_id>', methods=['GET'])
@login_required
def get_conversation(conversation_id):
    """获取特定对话的详细信息"""
    conversation = Conversation.query.filter_by(id=conversation_id, user_id=current_user.id).first()
    if not conversation:
        return jsonify({
            "error": True,
            "message": "对话不存在或无权访问"
        }), 404
    
    return jsonify({
        "conversation": conversation.to_dict()
    }), 200

@chat_bp.route('/conversations/<int:conversation_id>', methods=['PATCH'])
@login_required
def update_conversation(conversation_id):
    """更新对话信息"""
    try:
        conversation = Conversation.query.filter_by(id=conversation_id, user_id=current_user.id).first()
        if not conversation:
            return jsonify({
                "error": True,
                "message": "对话不存在或无权访问"
            }), 404
        
        data = request.get_json()
        
        # 更新标题
        if 'title' in data:
            conversation.title = data['title']
        
        # 更新模型
        if 'model' in data and data['model'] in [m["id"] for m in AVAILABLE_MODELS]:
            conversation.model = data['model']
        
        # 更新时间戳
        conversation.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "conversation": conversation.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新对话失败: {str(e)}")
        return jsonify({
            "error": True,
            "message": "更新对话失败"
        }), 500

@chat_bp.route('/conversations/<int:conversation_id>', methods=['DELETE'])
@login_required
def delete_conversation(conversation_id):
    """删除对话及其所有消息"""
    try:
        conversation = Conversation.query.filter_by(id=conversation_id, user_id=current_user.id).first()
        if not conversation:
            return jsonify({
                "error": True,
                "message": "对话不存在或无权访问"
            }), 404
        
        db.session.delete(conversation)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "对话删除成功"
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除对话失败: {str(e)}")
        return jsonify({
            "error": True,
            "message": "删除对话失败"
        }), 500

@chat_bp.route('/conversations/<int:conversation_id>/messages', methods=['GET'])
@login_required
def get_conversation_messages(conversation_id):
    """获取特定对话的所有消息"""
    try:
        conversation = Conversation.query.filter_by(id=conversation_id, user_id=current_user.id).first()
        if not conversation:
            return jsonify({
                "error": True,
                "message": "对话不存在或无权访问"
            }), 404
        
        # 获取该对话的所有消息
        messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at).all()
        
        # 处理消息数据
        result = [message.to_dict() for message in messages]
        
        return jsonify({
            "conversation": conversation.to_dict(),
            "messages": result
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取对话消息失败: {str(e)}")
        return jsonify({
            "error": True,
            "message": "获取对话消息失败"
        }), 500

@chat_bp.route('/conversations/<int:conversation_id>/messages', methods=['POST'])
@login_required
def add_message(conversation_id):
    """向特定对话添加新消息并获取AI回复"""
    try:
        conversation = Conversation.query.filter_by(id=conversation_id, user_id=current_user.id).first()
        if not conversation:
            return jsonify({
                "error": True,
                "message": "对话不存在或无权访问"
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                "error": True,
                "message": "无效的请求数据"
            }), 400
        
        # 获取用户消息内容和请求参数
        content = data.get('content')
        if not content:
            return jsonify({
                "error": True,
                "message": "消息内容不能为空"
            }), 400
        
        # 处理多模态内容
        role = data.get('role', 'user')
        media_type = data.get('media_type')  # 可以是 'image', 'audio', 'video'
        media_url = data.get('media_url')
        
        # 保存用户消息
        user_message = Message(
            role=role,
            content=content,
            conversation_id=conversation_id,
            media_type=media_type,
            media_url=media_url
        )
        
        db.session.add(user_message)
        db.session.commit()
        
        # 更新对话最后修改时间
        conversation.updated_at = datetime.utcnow()
        db.session.commit()
        
        # 准备发送给AI的消息
        # 获取最近的消息历史，限制上下文长度
        recent_messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at).all()[-10:]
        
        # 格式化消息历史为AI API所需格式
        formatted_messages = []
        system_message = {
            "role": "system",
            "content": "你是WordArt锦书AI助手，由通义千问大语言模型驱动，可以理解和回答各种问题。你的回答应当简洁、专业、有帮助性。遇到不确定或敏感的问题时，请诚实地表明自己的局限性。"
        }
        formatted_messages.append(system_message)
        
        for message in recent_messages:
            if message.media_type and message.media_url:
                # 处理多模态消息
                if message.media_type == 'image':
                    media_content = ai_service.get_image_content(message.media_url)
                    msg = ai_service.format_multimodal_message(message.role, message.content, media_content)
                    formatted_messages.append(msg)
                elif message.media_type == 'audio':
                    media_content = ai_service.get_audio_content(message.media_url)
                    msg = ai_service.format_multimodal_message(message.role, message.content, media_content)
                    formatted_messages.append(msg)
                elif message.media_type == 'video':
                    media_content = ai_service.get_video_content(message.media_url)
                    msg = ai_service.format_multimodal_message(message.role, message.content, media_content)
                    formatted_messages.append(msg)
                else:
                    # 不支持的媒体类型，作为普通文本处理
                    formatted_messages.append({
                        "role": message.role,
                        "content": message.content
                    })
            else:
                # 普通文本消息
                formatted_messages.append({
                    "role": message.role,
                    "content": message.content
                })
        
        # 选择合适的模型和方法处理请求
        model = conversation.model
        
        # 判断是否需要多模态处理
        is_multimodal_request = any(message.get('role') == 'user' and 
                                  isinstance(message.get('content'), list) 
                                  for message in formatted_messages)
        
        # 根据模型类型和请求内容调用不同的API方法
        if model == "qwen-omni-turbo" or is_multimodal_request:
            # 多模态模型或多模态请求
            response = ai_service.multimodal_completion(
                formatted_messages,
                model=model,
                stream=False  # 非流式API
            )
            
            # 处理响应
            try:
                # 由于multimodal_completion是生成器，我们需要获取第一个元素
                response_data = next(response)
                if response_data.get("error"):
                    return jsonify(response_data), 500
                
                # 处理AI响应
                ai_content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "AI无法生成回复")
                
                # 保存AI回复
                ai_message = Message(
                    role="assistant",
                    content=ai_content,
                    conversation_id=conversation_id
                )
                
                # 只有在消耗了token时才记录
                if "usage" in response_data:
                    tokens = response_data["usage"].get("total_tokens", 0)
                    ai_message.tokens = tokens
                
                db.session.add(ai_message)
                db.session.commit()
                
                # 返回结果
                return jsonify({
                    "message": ai_message.to_dict()
                }), 200
                
            except StopIteration:
                return jsonify({
                    "error": True,
                    "message": "AI生成回复失败"
                }), 500
                
        else:
            # 文本模型
            response = ai_service.text_completion(
                formatted_messages,
                model=model,
                stream=False  # 非流式API
            )
            
            # 检查响应是否有错误
            if response.get("error"):
                return jsonify(response), 500
            
            # 处理AI响应
            ai_content = response.get("choices", [{}])[0].get("message", {}).get("content", "AI无法生成回复")
            
            # 保存AI回复
            ai_message = Message(
                role="assistant",
                content=ai_content,
                conversation_id=conversation_id
            )
            
            # 只有在消耗了token时才记录
            if "usage" in response:
                tokens = response["usage"].get("total_tokens", 0)
                ai_message.tokens = tokens
            
            db.session.add(ai_message)
            db.session.commit()
            
            # 返回结果
            return jsonify({
                "message": ai_message.to_dict()
            }), 200
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"处理消息失败: {str(e)}")
        return jsonify({
            "error": True,
            "message": f"处理消息失败: {str(e)}"
        }), 500

@chat_bp.route('/conversations/<int:conversation_id>/stream', methods=['POST'])
@login_required
def stream_message(conversation_id):
    """向特定对话添加新消息并以流式方式获取AI回复"""
    try:
        conversation = Conversation.query.filter_by(id=conversation_id, user_id=current_user.id).first()
        if not conversation:
            return jsonify({
                "error": True,
                "message": "对话不存在或无权访问"
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                "error": True,
                "message": "无效的请求数据"
            }), 400
        
        # 获取用户消息内容和请求参数
        content = data.get('content')
        if not content:
            return jsonify({
                "error": True,
                "message": "消息内容不能为空"
            }), 400
        
        # 处理多模态内容
        role = data.get('role', 'user')
        media_type = data.get('media_type')  # 可以是 'image', 'audio', 'video'
        media_url = data.get('media_url')
        
        # 保存用户消息
        user_message = Message(
            role=role,
            content=content,
            conversation_id=conversation_id,
            media_type=media_type,
            media_url=media_url
        )
        
        db.session.add(user_message)
        db.session.commit()
        
        # 更新对话最后修改时间
        conversation.updated_at = datetime.utcnow()
        db.session.commit()
        
        # 准备发送给AI的消息
        # 获取最近的消息历史，限制上下文长度
        recent_messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at).all()[-10:]
        
        # 格式化消息历史为AI API所需格式
        formatted_messages = []
        system_message = {
            "role": "system",
            "content": "你是WordArt锦书AI助手，由通义千问大语言模型驱动，可以理解和回答各种问题。你的回答应当简洁、专业、有帮助性。遇到不确定或敏感的问题时，请诚实地表明自己的局限性。"
        }
        formatted_messages.append(system_message)
        
        for message in recent_messages:
            if message.media_type and message.media_url:
                # 处理多模态消息
                if message.media_type == 'image':
                    media_content = ai_service.get_image_content(message.media_url)
                    msg = ai_service.format_multimodal_message(message.role, message.content, media_content)
                    formatted_messages.append(msg)
                elif message.media_type == 'audio':
                    media_content = ai_service.get_audio_content(message.media_url)
                    msg = ai_service.format_multimodal_message(message.role, message.content, media_content)
                    formatted_messages.append(msg)
                elif message.media_type == 'video':
                    media_content = ai_service.get_video_content(message.media_url)
                    msg = ai_service.format_multimodal_message(message.role, message.content, media_content)
                    formatted_messages.append(msg)
                else:
                    # 不支持的媒体类型，作为普通文本处理
                    formatted_messages.append({
                        "role": message.role,
                        "content": message.content
                    })
            else:
                # 普通文本消息
                formatted_messages.append({
                    "role": message.role,
                    "content": message.content
                })
        
        # 选择合适的模型和生成方法
        model = conversation.model
        
        # 创建空的AI回复，用于后续流式更新
        ai_message = Message(
            role="assistant",
            content="",
            conversation_id=conversation_id
        )
        
        db.session.add(ai_message)
        db.session.commit()
        
        # 判断是否需要多模态处理
        is_multimodal_request = any(message.get('role') == 'user' and 
                                  isinstance(message.get('content'), list) 
                                  for message in formatted_messages)
        
        # 使用stream_with_context包装生成器，确保请求上下文在生成器中可用
        @stream_with_context
        def generate():
            # 流式响应的完整内容
            full_content = ""
            
            try:
                # 根据模型类型和请求内容调用不同的API方法
                if model == "qwen-omni-turbo" or is_multimodal_request:
                    # 多模态模型或多模态请求
                    try:
                        current_app.logger.info(f"开始Omni模型流式生成")
                        stream_response = ai_service.multimodal_completion(
                            formatted_messages,
                            model=model
                        )
                    except Exception as e:
                        current_app.logger.error(f"Omni模型流式生成失败: {str(e)}")
                        error_msg = json.dumps({
                            "error": True,
                            "message": f"Omni模型生成失败: {str(e)}"
                        })
                        yield f"data: {error_msg}\n\n"
                        return
                else:
                    # 文本模型
                    stream_response = ai_service.stream_text_completion(
                        formatted_messages,
                        model=model
                    )
                
                # 处理流式响应
                for chunk in stream_response:
                    # 检查是否有错误
                    if chunk.get("error"):
                        error_msg = json.dumps({
                            "error": True,
                            "message": chunk.get("message", "AI生成回复失败")
                        })
                        yield f"data: {error_msg}\n\n"
                        return
                    
                    # 获取内容增量
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                        delta = chunk["choices"][0].get("delta", {})
                        if delta and "content" in delta:
                            content_piece = delta["content"]
                            full_content += content_piece
                            
                            # 实时更新数据库中的消息
                            ai_message.content = full_content
                            db.session.commit()
                            
                            # 发送增量内容
                            yield f"data: {json.dumps({'content': content_piece})}\n\n"
                    
                    # 记录用量信息
                    if "usage" in chunk:
                        ai_message.tokens = chunk["usage"].get("total_tokens", 0)
                        db.session.commit()
                
                # 完成消息
                yield f"data: {json.dumps({'done': True})}\n\n"
                
            except Exception as e:
                current_app.logger.error(f"流式生成失败: {str(e)}")
                error_msg = json.dumps({
                    "error": True,
                    "message": f"流式生成失败: {str(e)}"
                })
                yield f"data: {error_msg}\n\n"
                
                # 如果生成失败，设置回复为错误信息
                ai_message.content = f"生成失败: {str(e)}"
                db.session.commit()
            
            yield "data: [DONE]\n\n"
        
        # 返回流式响应
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"处理流式消息失败: {str(e)}")
        return jsonify({
            "error": True,
            "message": f"处理流式消息失败: {str(e)}"
        }), 500

@chat_bp.route('/completions', methods=['POST'])
def api_completions():
    """API调用模型生成回复（无需登录，适用于本地模式）"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "error": True,
                "message": "无效的请求数据"
            }), 400
        
        # 验证请求字段
        required_fields = ['model', 'messages']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": True,
                    "message": f"缺少必需字段: {field}"
                }), 400
        
        model = data['model']
        messages = data['messages']
        
        # 验证模型是否支持
        if model not in [m["id"] for m in AVAILABLE_MODELS]:
            return jsonify({
                "error": True,
                "message": f"不支持的模型: {model}"
            }), 400
        
        # 记录API调用日志
        current_app.logger.info(f"API调用: 模型={model}, 消息数量={len(messages) if messages is not None else '未知(None)'}")
        
        # --- FIX: 增加对 messages 是否为列表的检查 ---
        if not isinstance(messages, list):
            current_app.logger.error(f"请求中的 'messages' 字段不是列表，而是: {type(messages)}")
            return jsonify({
                "error": True,
                "message": "请求中的 'messages' 必须是一个列表"
            }), 400
        # --- FIX END ---
        
        # 控制是否使用流式返回
        use_stream = data.get('stream', False)
        
        # 检查是否是多模态模型
        is_multimodal = model == 'qwen-omni-turbo'
        
        # 对于多模态模型，特殊处理消息格式
        if is_multimodal:
            # 检查消息格式是否正确 (检查 role 和 msg 类型)
            for msg in messages:
                # --- FIX: 确保 msg 是字典 --- 
                if not isinstance(msg, dict):
                    current_app.logger.error(f"消息列表中的项目不是字典: {type(msg)}, 内容: {msg}")
                    return jsonify({"error": True, "message": "消息列表包含无效项"}), 400
                # --- FIX END ---
                
                if 'role' not in msg or not msg['role']:
                    return jsonify({
                        "error": True,
                        "message": "消息缺少role字段"
                    }), 400
            
            # 调用多模态服务
            try:
                @stream_with_context
                def generate():
                    try:
                        current_app.logger.info(f"开始Omni模型流式生成")
                        stream_response = ai_service.multimodal_completion(
                            messages=messages,
                            model=model,
                            stream=True,
                            temperature=data.get('temperature', 0.7),
                            max_tokens=data.get('max_tokens')
                        )
                        
                        for chunk in stream_response:
                            if chunk.get("error"):
                                error_msg = json.dumps({
                                    "error": True,
                                    "message": chunk.get("message", "AI生成回复失败")
                                })
                                current_app.logger.error(f"Omni模型生成错误: {error_msg}")
                                yield f"data: {error_msg}\n\n"
                                return
                            
                            yield f"data: {json.dumps(chunk)}\n\n"
                        
                    except Exception as e:
                        current_app.logger.error(f"Omni模型流式生成失败: {str(e)}")
                        error_msg = json.dumps({
                            "error": True,
                            "message": f"Omni模型生成失败: {str(e)}"
                        })
                        yield f"data: {error_msg}\n\n"
                    
                    yield "data: [DONE]\n\n"
                
                return Response(
                    generate(),
                    mimetype='text/event-stream',
                    headers={
                        'Cache-Control': 'no-cache',
                        'Connection': 'keep-alive',
                        'X-Accel-Buffering': 'no'
                    }
                )
            except Exception as e:
                current_app.logger.error(f"Omni模型调用失败: {str(e)}")
                return jsonify({
                    "error": True,
                    "message": f"Omni模型处理失败: {str(e)}"
                }), 500
        
        # --- FIX: 添加 else 条件，确保文本模型处理只在非多模态时执行 ---
        else:
            # 对于普通文本模型，进行标准处理
            # 检查消息格式
            for msg in messages:
                if 'role' not in msg or 'content' not in msg:
                    return jsonify({
                        "error": True,
                        "message": "消息格式错误，需要包含role和content字段"
                    }), 400
                
                # 确保content是字符串
                if not isinstance(msg['content'], str):
                    # 这里之前会错误地转换数组，现在因为在 else 分支，不会影响多模态
                    current_app.logger.warning(f"消息内容不是字符串，强制转换为字符串: {type(msg['content'])}")
                    msg['content'] = str(msg['content'])
            
            # 根据请求选择流式或非流式响应
            if use_stream:
                # 流式返回
                def generate():
                    for chunk in ai_service.stream_text_completion(
                        messages=messages,
                        model=model,
                        temperature=data.get('temperature', 0.7),
                        max_tokens=data.get('max_tokens')
                    ):
                        if 'error' in chunk:
                            yield f"data: {json.dumps(chunk)}\n\n"
                            break
                        
                        yield f"data: {json.dumps(chunk)}\n\n"
                    
                    yield "data: [DONE]\n\n"
                
                return Response(
                    stream_with_context(generate()),
                    mimetype='text/event-stream'
                )
            else:
                # 非流式返回
                response = ai_service.text_completion(
                    messages=messages,
                    model=model,
                    stream=False,
                    temperature=data.get('temperature', 0.7),
                    max_tokens=data.get('max_tokens')
                )
                
                return jsonify(response)
            
    except Exception as e:
        current_app.logger.error(f"处理API请求失败: {str(e)}")
        return jsonify({
            "error": True,
            "message": f"处理请求失败: {str(e)}"
        }), 500

@chat_bp.route('/stream-completions', methods=['POST'])
@login_required
def stream_completion():
    """单次流式聊天完成，不保存对话历史"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "error": True,
                "message": "无效的请求数据"
            }), 400
        
        # 获取消息内容和模型
        messages = data.get('messages', [])
        model = data.get('model', 'qwen-max-latest')
        
        # 验证参数
        if not messages:
            return jsonify({
                "error": True,
                "message": "消息列表不能为空"
            }), 400
        
        if model not in [m["id"] for m in AVAILABLE_MODELS]:
            return jsonify({
                "error": True,
                "message": f"不支持的模型: {model}"
            }), 400
        
        # 添加系统提示
        if not any(m.get('role') == 'system' for m in messages):
            system_message = {
                "role": "system",
                "content": "你是WordArt锦书AI助手，由通义千问大语言模型驱动，可以理解和回答各种问题。你的回答应当简洁、专业、有帮助性。遇到不确定或敏感的问题时，请诚实地表明自己的局限性。"
            }
            messages.insert(0, system_message)
        
        # 判断是否需要多模态处理
        is_multimodal_request = any(message.get('role') == 'user' and 
                                  isinstance(message.get('content'), list) 
                                  for message in messages)
        
        # 使用stream_with_context包装生成器，确保请求上下文在生成器中可用
        @stream_with_context
        def generate():
            try:
                # 根据模型类型和请求内容调用不同的API方法
                if model == "qwen-omni-turbo" or is_multimodal_request:
                    # 多模态模型或多模态请求
                    stream_response = ai_service.multimodal_completion(
                        messages,
                        model=model
                    )
                else:
                    # 文本模型
                    stream_response = ai_service.stream_text_completion(
                        messages,
                        model=model
                    )
                
                # 处理流式响应
                for chunk in stream_response:
                    # 检查是否有错误
                    if chunk.get("error"):
                        error_msg = json.dumps({
                            "error": True,
                            "message": chunk.get("message", "AI生成回复失败")
                        })
                        yield f"data: {error_msg}\n\n"
                        return
                    
                    # 转发AI响应
                    yield f"data: {json.dumps(chunk)}\n\n"
                
            except Exception as e:
                current_app.logger.error(f"流式生成失败: {str(e)}")
                error_msg = json.dumps({
                    "error": True,
                    "message": f"流式生成失败: {str(e)}"
                })
                yield f"data: {error_msg}\n\n"
            
            yield "data: [DONE]\n\n"
        
        # 返回流式响应
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        current_app.logger.error(f"处理流式聊天失败: {str(e)}")
        return jsonify({
            "error": True,
            "message": f"处理流式聊天失败: {str(e)}"
        }), 500

@chat_bp.route('/omni-completions', methods=['POST'])
def api_omni_completions():
    """API调用Omni模型生成回复，专用于多模态模型"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "error": True,
                "message": "无效的请求数据"
            }), 400
        
        # 验证请求字段
        required_fields = ['model', 'messages']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": True,
                    "message": f"缺少必需字段: {field}"
                }), 400
        
        model = data['model']
        messages = data['messages']
        
        # 验证是否为Omni模型
        if model != "qwen-omni-turbo":
            return jsonify({
                "error": True,
                "message": f"此端点仅支持qwen-omni-turbo模型"
            }), 400
        
        # 记录API调用日志
        current_app.logger.info(f"Omni模型API调用: 消息数量={len(messages)}")
        
        # 检查消息格式是否正确
        for msg in messages:
            if 'role' not in msg or not msg['role']:
                return jsonify({
                    "error": True,
                    "message": "消息缺少role字段"
                }), 400
            
            # 检查内容格式
            if 'content' not in msg:
                return jsonify({
                    "error": True,
                    "message": "消息缺少content字段"
                }), 400
        
        # 添加系统消息
        if not any(msg.get('role') == 'system' for msg in messages):
            system_message = {
                "role": "system", 
                "content": "你是WordArt锦书AI助手，由通义千问大语言模型驱动，可以理解文本和图像。"
            }
            messages.insert(0, system_message)
        
        # 使用stream_with_context包装生成器，确保请求上下文在生成器中可用
        @stream_with_context
        def generate():
            try:
                current_app.logger.info(f"开始Omni模型流式生成")
                # 多模态模型请求
                stream_response = ai_service.multimodal_completion(
                    messages,
                    model=model,
                    stream=True,
                    temperature=data.get('temperature', 0.7),
                    max_tokens=data.get('max_tokens')
                )
                
                # 处理流式响应
                for chunk in stream_response:
                    # 检查是否有错误
                    if chunk.get("error"):
                        error_msg = json.dumps({
                            "error": True,
                            "message": chunk.get("message", "AI生成回复失败")
                        })
                        current_app.logger.error(f"Omni模型生成错误: {error_msg}")
                        yield f"data: {error_msg}\n\n"
                        return
                    
                    # 转发AI响应
                    yield f"data: {json.dumps(chunk)}\n\n"
                
            except Exception as e:
                current_app.logger.error(f"Omni模型流式生成失败: {str(e)}")
                error_msg = json.dumps({
                    "error": True,
                    "message": f"Omni模型生成失败: {str(e)}"
                })
                yield f"data: {error_msg}\n\n"
            
            yield "data: [DONE]\n\n"
        
        # 返回流式响应
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        current_app.logger.error(f"处理Omni模型请求失败: {str(e)}")
        return jsonify({
            "error": True,
            "message": f"处理Omni模型请求失败: {str(e)}"
        }), 500

@chat_bp.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传"""
    try:
        # 添加请求调试日志
        current_app.logger.info(f"接收到文件上传请求，Content-Type: {request.content_type}")
        current_app.logger.info(f"请求表单数据: {list(request.form.keys())}")
        current_app.logger.info(f"请求文件: {list(request.files.keys())}")
        
        # 输出详细的请求信息
        for name, file_storage in request.files.items():
            current_app.logger.info(f"文件字段: {name}, 文件名: {file_storage.filename}, 大小: {file_storage.content_length if hasattr(file_storage, 'content_length') else '未知'}")
        
        # 检查是否有文件
        if 'file' not in request.files:
            current_app.logger.error("没有在请求中找到'file'字段")
            # 记录所有请求头信息以便调试
            headers_info = '\n'.join([f"{k}: {v}" for k, v in request.headers.items()])
            current_app.logger.error(f"请求头信息:\n{headers_info}")
            return jsonify({
                "error": True,
                "message": "没有上传文件"
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            current_app.logger.error("上传的文件名为空")
            return jsonify({
                "error": True,
                "message": "没有选择文件"
            }), 400
        
        # 记录文件信息
        current_app.logger.info(f"接收到文件: {file.filename}, MIME类型: {file.content_type}")
        
        # 检查文件类型
        if not allowed_file(file.filename):
            current_app.logger.error(f"不支持的文件类型: {file.filename}")
            return jsonify({
                "error": True,
                "message": "不支持的文件类型"
            }), 400
        
        # 检查文件大小
        try:
            file_content = file.read()
            file_size = len(file_content)
            current_app.logger.info(f"文件大小: {file_size} 字节")
            file.seek(0)  # 重置文件指针
            
            if file_size > MAX_CONTENT_LENGTH:
                current_app.logger.error(f"文件过大: {file_size} > {MAX_CONTENT_LENGTH}")
                return jsonify({
                    "error": True,
                    "message": f"文件大小超过限制 ({MAX_CONTENT_LENGTH/1024/1024:.1f}MB)"
                }), 400
        except Exception as e:
            current_app.logger.error(f"读取文件内容失败: {str(e)}")
            return jsonify({
                "error": True,
                "message": f"读取文件内容失败: {str(e)}"
            }), 400
        
        # 使用绝对路径确保上传目录存在
        upload_path = os.path.abspath(UPLOAD_FOLDER)
        current_app.logger.info(f"使用上传路径: {upload_path}")
        if not os.path.exists(upload_path):
            current_app.logger.info(f"创建上传目录: {upload_path}")
            os.makedirs(upload_path, exist_ok=True)
        
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        
        # 根据文件类型选择子目录
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
            sub_dir = 'images'
        elif file_ext in ['.mp3', '.wav', '.m4a']:
            sub_dir = 'audio'
        elif file_ext in ['.mp4', '.mov', '.avi']:
            sub_dir = 'video'
        else:
            sub_dir = 'documents'
            
        sub_path = os.path.join(upload_path, sub_dir)
        if not os.path.exists(sub_path):
            current_app.logger.info(f"创建子目录: {sub_path}")
            os.makedirs(sub_path, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(sub_path, unique_filename)
        current_app.logger.info(f"保存文件到: {file_path}")
        try:
            file.save(file_path)
            
            # 验证文件已保存
            if not os.path.exists(file_path):
                current_app.logger.error(f"文件保存失败: {file_path}")
                return jsonify({
                    "error": True,
                    "message": "文件保存失败，路径不存在"
                }), 500
                
            # 返回文件URL (使用相对路径，前端可以直接访问)
            file_url = f"/api/chat/uploads/{sub_dir}/{unique_filename}"
            
            current_app.logger.info(f"文件上传成功: {file_url}")
            
            return jsonify({
                "url": file_url,
                "filename": filename
            }), 200
        except Exception as save_error:
            current_app.logger.error(f"保存文件时出错: {str(save_error)}", exc_info=True)
            return jsonify({
                "error": True,
                "message": f"保存文件失败: {str(save_error)}"
            }), 500
        
    except Exception as e:
        current_app.logger.error(f"文件上传失败: {str(e)}", exc_info=True)
        return jsonify({
            "error": True,
            "message": f"文件上传失败: {str(e)}"
        }), 500

@chat_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """提供上传文件的访问"""
    try:
        # 使用绝对路径
        upload_path = os.path.abspath(UPLOAD_FOLDER)
        current_app.logger.info(f"尝试访问文件: {filename}, 上传目录: {upload_path}")
        
        # 检查文件是否存在
        if "/" in filename:
            # 如果包含路径(子目录)
            subdir = filename.split('/')[0]
            name = '/'.join(filename.split('/')[1:])
            full_path = os.path.join(upload_path, filename)
            current_app.logger.info(f"查找子目录文件: {full_path}")
            
            if os.path.exists(full_path):
                return send_from_directory(os.path.join(upload_path, subdir), name)
        else:
            # 尝试在所有子目录中查找
            for subdir in ['images', 'audio', 'video', 'documents']:
                file_path = os.path.join(upload_path, subdir, filename)
                current_app.logger.info(f"查找文件: {file_path}")
                if os.path.exists(file_path):
                    return send_from_directory(os.path.join(upload_path, subdir), filename)
        
        # 文件不存在
        current_app.logger.error(f"找不到文件: {filename}")
        return jsonify({
            "error": True,
            "message": f"文件不存在: {filename}"
        }), 404
    except Exception as e:
        current_app.logger.error(f"访问上传文件失败: {str(e)}", exc_info=True)
        return jsonify({
            "error": True,
            "message": f"文件不存在: {str(e)}"
        }), 404 