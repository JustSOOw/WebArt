"""初始数据库迁移

Revision ID: 001
Revises: 
Create Date: 2025-03-10 13:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 创建用户表
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=64), nullable=True),
        sa.Column('email', sa.String(length=120), nullable=True),
        sa.Column('password_hash', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # 创建图片表
    op.create_table('images',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.String(length=64), nullable=True),
        sa.Column('url', sa.String(length=255), nullable=False),
        sa.Column('surname', sa.String(length=10), nullable=False),
        sa.Column('style', sa.String(length=50), nullable=True),
        sa.Column('style_name', sa.String(length=50), nullable=True),
        sa.Column('prompt', sa.Text(), nullable=True),
        sa.Column('ref_image_url', sa.String(length=255), nullable=True),
        sa.Column('font_name', sa.String(length=50), nullable=True),
        sa.Column('ttf_url', sa.String(length=255), nullable=True),
        sa.Column('text_strength', sa.Float(), nullable=True),
        sa.Column('text_inverse', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_images_task_id'), 'images', ['task_id'], unique=False)


def downgrade():
    # 删除表
    op.drop_index(op.f('ix_images_task_id'), table_name='images')
    op.drop_table('images')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users') 