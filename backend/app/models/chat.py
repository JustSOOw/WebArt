r'''
 * @Author: JustSOOw wang813104@outlook.com
 * @Date: 2025-03-22 18:37:39
 * @LastEditors: JustSOOw wang813104@outlook.com
 * @LastEditTime: 2025-03-23 12:01:03
 * @FilePath: \WebArt\backend\app\models\chat.py
 * @Description: 
 * @
 * @Copyright (c) 2025 by Furdow, All Rights Reserved. 
'''
from datetime import datetime
from app import db

class Conversation(db.Model):
    """对话会话模型，保存用户与AI的对话会话信息"""
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, default='新对话')
    model = db.Column(db.String(50), nullable=False, default='qwen-max-latest')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 外键关联
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    # 反向引用，建立与Message的一对多关系
    messages = db.relationship('Message', backref='conversation', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Conversation {self.id} - {self.title}>'
    
    def to_dict(self):
        """将对象转换为字典，方便JSON序列化"""
        return {
            'id': self.id,
            'title': self.title,
            'model': self.model,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'user_id': self.user_id
        }

class Message(db.Model):
    """对话消息模型，保存对话中的每条消息"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = db.Column(db.Text, nullable=False)
    media_type = db.Column(db.String(20), nullable=True)  # 'image', 'audio', 'video' 多模态支持
    media_url = db.Column(db.String(255), nullable=True)  # 媒体文件URL
    tokens = db.Column(db.Integer, nullable=True)  # 记录token数量
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 外键关联
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    
    def __repr__(self):
        return f'<Message {self.id} - {self.role}>'
    
    def to_dict(self):
        """将对象转换为字典，方便JSON序列化"""
        result = {
            'id': self.id,
            'role': self.role,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'conversation_id': self.conversation_id
        }
        
        # 只有在存在媒体信息时才添加这些字段
        if self.media_type:
            result['media_type'] = self.media_type
        if self.media_url:
            result['media_url'] = self.media_url
        if self.tokens:
            result['tokens'] = self.tokens
            
        return result 