'''
Author: JustSOOw wang813104@outlook.com
Date: 2025-03-10 13:45:37
LastEditors: JustSOOw wang813104@outlook.com
LastEditTime: 2025-03-12 22:08:23
FilePath: /WebArt/backend/manage.py
Description: 

Copyright (c) 2025 by Furdow, All Rights Reserved. 
'''
import os
import click
from flask.cli import FlaskGroup
from app import create_app, db
from app.models import User, Image
from sqlalchemy import inspect

app = create_app()

cli = FlaskGroup(app)

@cli.command('init-db')
def init_db():
    """初始化数据库"""
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
            click.echo("已创建测试用户: test_user (密码: password123)")
        
        # 检查数据库中的表 - 使用SQLAlchemy 1.4+兼容的方式
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        click.echo(f"数据库中的表: {', '.join(tables)}")
        
        # 检查用户数量
        user_count = User.query.count()
        click.echo(f"用户数量: {user_count}")
        
        # 检查图片数量
        image_count = Image.query.count()
        click.echo(f"图片数量: {image_count}")
        
        click.echo("数据库初始化完成!")

@cli.command('create-admin')
@click.argument('username')
@click.argument('email')
@click.argument('password')
def create_admin(username, email, password):
    """创建管理员用户"""
    with app.app_context():
        # 检查用户是否已存在
        if User.query.filter_by(username=username).first():
            click.echo(f"用户 {username} 已存在!")
            return
        
        if User.query.filter_by(email=email).first():
            click.echo(f"邮箱 {email} 已被使用!")
            return
        
        # 创建管理员用户
        admin = User(
            username=username,
            email=email,
            password=password
        )
        db.session.add(admin)
        db.session.commit()
        click.echo(f"管理员用户 {username} 创建成功!")

@cli.command('list-users')
def list_users():
    """列出所有用户"""
    with app.app_context():
        users = User.query.all()
        if not users:
            click.echo("没有用户!")
            return
        
        click.echo("用户列表:")
        for user in users:
            click.echo(f"ID: {user.id}, 用户名: {user.username}, 邮箱: {user.email}, 创建时间: {user.created_at}")

@cli.command('list-images')
@click.option('--limit', default=10, help='显示的图片数量')
def list_images(limit):
    """列出最近的图片"""
    with app.app_context():
        images = Image.query.order_by(Image.created_at.desc()).limit(limit).all()
        if not images:
            click.echo("没有图片!")
            return
        
        click.echo(f"最近 {len(images)} 张图片:")
        for image in images:
            click.echo(f"ID: {image.id}, 姓氏: {image.surname}, 风格: {image.style_name}, 创建时间: {image.created_at}")

if __name__ == '__main__':
    cli() 