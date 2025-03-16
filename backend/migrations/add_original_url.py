r'''
 * @Author: JustSOOw wang813104@outlook.com
 * @Date: 2025-03-15 16:17:29
 * @LastEditors: JustSOOw wang813104@outlook.com
 * @LastEditTime: 2025-03-16 14:47:05
 * @FilePath: \WebArt\backend\migrations\add_original_url.py
 * @Description: 
 * @
 * @Copyright (c) 2025 by Furdow, All Rights Reserved. 
'''

'''
数据库迁移脚本：添加original_url字段到images表
'''
import os
import sqlite3
from flask import Flask
from app import create_app

def run_migration():
    """运行数据库迁移"""
    app = create_app()
    
    with app.app_context():
        # 获取数据库路径
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        # 如果是相对路径，转换为绝对路径
        if not os.path.isabs(db_path):
            db_path = os.path.join(app.root_path, db_path)
        
        print(f"数据库路径: {db_path}")
        
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # 检查字段是否已存在
            cursor.execute("PRAGMA table_info(images)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'original_url' not in columns:
                print("添加 original_url 字段到 images 表...")
                cursor.execute("ALTER TABLE images ADD COLUMN original_url TEXT")
                conn.commit()
                print("字段添加成功！")
            else:
                print("original_url 字段已存在，无需添加")
            
        except Exception as e:
            print(f"迁移失败: {str(e)}")
            conn.rollback()
        finally:
            conn.close()

if __name__ == '__main__':
    run_migration() 