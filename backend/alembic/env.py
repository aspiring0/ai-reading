"""
Alembic 异步迁移环境配置

默认的 env.py 是同步的，这里改写为异步模式以配合 asyncpg 驱动。
迁移时会自动检测 app/models/ 下的所有 ORM 模型来生成迁移脚本。
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.config import settings
from app.database import Base

# 导入所有模型，让 Alembic 能检测到它们
# 每添加新模型文件时，在这里 import 一次
# from app.models.user import User  # noqa: F401  — Phase 3 启用
from app.models.article import Article, ArticleSegment  # noqa: F401
# from app.models.article import Article, ArticleSegment  # noqa: F401  — Phase 1 启用

config = context.config

# 设置数据库连接串，优先使用环境变量（.env 文件中的 DATABASE_URL）
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# target_metadata 是 Alembic 自动生成迁移的依据
# 它包含所有 ORM 模型的表定义
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """离线模式：生成 SQL 脚本而不连接数据库（用于审查 SQL）。"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """在线模式：连接数据库并执行迁移（异步版本）。"""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """在线模式入口，启动异步事件循环执行迁移。"""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
