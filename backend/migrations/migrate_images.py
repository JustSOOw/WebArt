"""
图片数据迁移脚本

此脚本用于：
1. 添加original_url字段到images表
2. 下载现有图片到本地服务器
"""

import os
import sys
import sqlite3
from flask import Flask
from app import create_app, db
from app.utils import download_remote_image

def migrate_images():
    """执行图片数据迁移"""
    print("开始图片数据迁移...")
    
    # 创建应用上下文
    app = create_app()
    with app.app_context():
        # 检查数据库中是否已有original_url字段
        conn = sqlite3.connect(app.config['DATABASE_URI'].replace('sqlite:///', ''))
        cursor = conn.cursor()
        
        # 获取images表的列信息
        cursor.execute("PRAGMA table_info(images)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # 如果没有original_url字段，添加它
        if 'original_url' not in columns:
            print("添加original_url字段到images表...")
            cursor.execute("ALTER TABLE images ADD COLUMN original_url TEXT")
            conn.commit()
        
        # 获取所有图片记录
        cursor.execute("SELECT id, url FROM images")
        images = cursor.fetchall()
        
        print(f"找到 {len(images)} 张图片记录")
        
        # 下载图片并更新记录
        for image_id, url in images:
            # 如果URL是本地路径，跳过
            if url.startswith('/api/static/uploads/'):
                continue
                
            print(f"处理图片 ID: {image_id}, URL: {url}")
            
            # 下载图片到本地
            try:
                local_url = download_remote_image(url, 'generated')
                
                # 更新记录
                cursor.execute(
                    "UPDATE images SET original_url = ?, url = ? WHERE id = ?",
                    (url, local_url, image_id)
                )
                conn.commit()
                print(f"  ✓ 成功下载并更新图片 ID: {image_id}")
            except Exception as e:
                print(f"  ✗ 处理图片 ID: {image_id} 失败: {str(e)}")
        
        conn.close()
        print("图片数据迁移完成")

if __name__ == "__main__":
    migrate_images() 