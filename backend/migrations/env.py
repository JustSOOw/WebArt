r'''
 * @Author: JustSOOw wang813104@outlook.com
 * @Date: 2025-03-10 13:46:10
 * @LastEditors: JustSOOw wang813104@outlook.com
 * @LastEditTime: 2025-03-16 14:52:50
 * @FilePath: \WebArt\backend\migrations\env.py
 * @Description: alembic环境文件
 * @
 * @Copyright (c) 2025 by Furdow, All Rights Reserved. 
'''
from __future__ import with_statement

import logging
from logging.config import fileConfig

from flask import current_app

from alembic import context

# 这是Alembic配置对象，它提供了对正在使用的.ini文件中的值的访问
config = context.config

# 解析Python日志的配置文件
# 这行代码基本上设置了日志记录器
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# 在这里添加你的模型的MetaData对象
# 用于'autogenerate'支持
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
config.set_main_option(
    'sqlalchemy.url',
    str(current_app.extensions['migrate'].db.get_engine().url).replace(
        '%', '%%'))
target_metadata = current_app.extensions['migrate'].db.metadata

# 可以获取配置中的其他值，根据env.py的需要定义：
# my_important_option = config.get_main_option("my_important_option")
# ... 等等


def run_migrations_offline():
    """以'离线'模式运行迁移。

    这只需配置一个URL而不是引擎，
    尽管这里也可以接受引擎。通过跳过引擎创建，
    我们甚至不需要DBAPI可用。

    这里对context.execute()的调用会将给定的字符串
    输出到脚本输出。
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """以'在线'模式运行迁移。

    在这种情况下，我们需要创建一个引擎
    并将连接与上下文关联。
    """

    # 这个回调用于防止在没有模式更改时
    # 自动生成迁移
    # 参考：http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('未检测到模式变化。')

    connectable = current_app.extensions['migrate'].db.get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
            **current_app.extensions['migrate'].configure_args
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 