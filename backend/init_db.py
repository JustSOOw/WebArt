r'''
 * @Author: JustSOOw wang813104@outlook.com
 * @Date: 2025-03-10 13:45:37
 * @LastEditors: JustSOOw wang813104@outlook.com
 * @LastEditTime: 2025-03-15 16:41:45
 * @FilePath: \WebArt\backend\init_db.py
 * @Description: 
 * @
 * @Copyright (c) 2025 by Furdow, All Rights Reserved. 
'''

import os
import sys
import uuid
import datetime
from flask import Flask
from app import create_app, db
from app.models import User, Image
from sqlalchemy import inspect, text

def init_db():
    """初始化数据库"""
    app = create_app()
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 检查是否已有用户
        if User.query.first() is None:
            # 创建一个测试用户
            test_user = User(
                username='test_user',
                email='test@example.com',
                password='password123'
            )
            db.session.add(test_user)
            db.session.commit()
            print("已创建测试用户: test_user (密码: password123)")
        
        # 检查数据库中的表 - 使用SQLAlchemy 1.4+兼容的方式
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"数据库中的表: {', '.join(tables)}")
        
        # 检查用户数量
        user_count = User.query.count()
        print(f"用户数量: {user_count}")
        
        # 检查图片数量 - 使用原始SQL避免ORM错误
        try:
            # 尝试使用ORM
            image_count = Image.query.count()
            print(f"图片数量: {image_count}")
        except Exception as e:
            print(f"使用ORM获取图片数量失败: {str(e)}")
            try:
                # 使用原始SQL
                result = db.session.execute(text("SELECT COUNT(*) FROM images"))
                image_count = result.scalar()
                print(f"图片数量(SQL): {image_count}")
                
                # 检查并添加original_url列
                columns = [column['name'] for column in inspector.get_columns('images')]
                if 'original_url' not in columns:
                    print("添加original_url列到images表...")
                    db.session.execute(text("ALTER TABLE images ADD COLUMN original_url TEXT"))
                    db.session.commit()
                    print("列添加成功！")
            except Exception as inner_e:
                print(f"获取图片数量失败: {str(inner_e)}")
        
        print("数据库初始化完成!")

if __name__ == '__main__':
    init_db() 