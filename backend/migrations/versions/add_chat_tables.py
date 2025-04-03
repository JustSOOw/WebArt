r'''
 * @Author: JustSOOw wang813104@outlook.com
 * @Date: 2025-03-22 18:38:07
 * @LastEditors: JustSOOw wang813104@outlook.com
 * @LastEditTime: 2025-03-24 14:28:41
 * @FilePath: \WebArt\backend\migrations\versions\add_chat_tables.py
 * @Description: 
 * @
 * @Copyright (c) 2025 by Furdow, All Rights Reserved. 
'''
"""添加聊天表

Revision ID: add_chat_tables
Revises: 
Create Date: 2025-03-20 10:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_chat_tables'
down_revision = None  # 需要根据实际情况修改
branch_labels = None
depends_on = None


def upgrade():
    # 创建对话会话表
    op.create_table('conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False, server_default='新对话'),
        sa.Column('model', sa.String(length=50), nullable=False, server_default='qwen-max-latest'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建聊天消息表
    op.create_table('messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('media_type', sa.String(length=20), nullable=True),
        sa.Column('media_url', sa.String(length=255), nullable=True),
        sa.Column('tokens', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 添加索引以提高查询性能
    op.create_index(op.f('ix_conversations_user_id'), 'conversations', ['user_id'], unique=False)
    op.create_index(op.f('ix_messages_conversation_id'), 'messages', ['conversation_id'], unique=False)


def downgrade():
    # 删除索引
    op.drop_index(op.f('ix_messages_conversation_id'), table_name='messages')
    op.drop_index(op.f('ix_conversations_user_id'), table_name='conversations')
    
    # 删除表
    op.drop_table('messages')
    op.drop_table('conversations') 