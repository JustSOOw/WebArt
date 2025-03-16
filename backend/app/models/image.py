'''
Author: JustSOOw wang813104@outlook.com
Date: 2025-03-10 13:45:37
LastEditors: JustSOOw wang813104@outlook.com
LastEditTime: 2025-03-12 22:08:23
FilePath: /WebArt/backend/app/models/image.py
Description: 

Copyright (c) 2025 by Furdow, All Rights Reserved. 
'''
from datetime import datetime
from app import db

class Image(db.Model):
    __tablename__ = 'images'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(64), index=True)
    url = db.Column(db.String(255), nullable=False)
    original_url = db.Column(db.String(255), nullable=True)
    surname = db.Column(db.String(10), nullable=False)
    style = db.Column(db.String(50))
    style_name = db.Column(db.String(50))
    prompt = db.Column(db.Text, nullable=True)
    ref_image_url = db.Column(db.String(255), nullable=True)
    font_name = db.Column(db.String(50), nullable=True)
    ttf_url = db.Column(db.String(255), nullable=True)
    text_strength = db.Column(db.Float, nullable=True)
    text_inverse = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    def __repr__(self):
        return f'<Image {self.id} - {self.surname}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'url': self.url,
            'original_url': self.original_url,
            'surname': self.surname,
            'style': self.style,
            'style_name': self.style_name,
            'prompt': self.prompt,
            'ref_image_url': self.ref_image_url,
            'font_name': self.font_name,
            'ttf_url': self.ttf_url,
            'text_strength': self.text_strength,
            'text_inverse': self.text_inverse,
            'created_at': self.created_at.isoformat(),
            'user_id': self.user_id
        } 