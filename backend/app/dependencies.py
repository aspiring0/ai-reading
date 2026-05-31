"""
共享依赖注入

FastAPI 的依赖注入系统，提供通用的数据库会话、Redis 连接和用户认证。
API 端点通过 Depends() 使用，方便测试时替换为 mock 对象。

使用方式：
    @router.get("/articles")
    async def list_articles(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        ...
"""

from collections.abc import AsyncGenerator

import redis.asyncio as aioredis
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """提供数据库会话 — 与 database.py 中的 get_db 相同逻辑，作为统一入口。"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_redis(request: Request) -> aioredis.Redis:
    """提供 Redis 连接 — 从 app.state 获取（在 main.py lifespan 中创建）。"""
    return request.app.state.redis


async def get_current_user() -> None:
    """获取当前认证用户 — 暂为桩，Phase 3 实现完整 JWT 认证后替换。

    Phase 3 实现逻辑：
        1. 从请求头提取 Bearer token
        2. 用 PyJWT 解码验证
        3. 从数据库查询用户
        4. 返回 User 对象
    """
    return None
