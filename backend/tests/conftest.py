"""
测试配置 — 提供共享的测试 fixture。

conftest.py 是 pytest 的特殊文件，里面的 fixture 所有测试文件都能用。
"""

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.dependencies import get_db, get_redis
from app.main import app

# 测试数据库 — 用开发库，每个测试回滚不会污染
TEST_DATABASE_URL = "postgresql+asyncpg://aireading:aireading_dev@localhost:5432/ai_reading"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """提供事务性的数据库会话 — 测试结束后自动回滚。"""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
def mock_redis() -> AsyncMock:
    """提供 mock Redis — 测试时不连真实 Redis，避免缓存干扰。"""
    redis = AsyncMock()
    redis.get.return_value = None  # 默认缓存未命中
    redis.set.return_value = True
    redis.delete.return_value = 1
    return redis


@pytest_asyncio.fixture
async def client(db_session: AsyncSession, mock_redis: AsyncMock) -> AsyncGenerator[AsyncClient, None]:
    """提供异步 HTTP 测试客户端，使用测试数据库和 mock Redis。

    覆盖 FastAPI 的 get_db 和 get_redis 依赖。
    """

    async def override_get_db():
        yield db_session

    def override_get_redis():
        return mock_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
