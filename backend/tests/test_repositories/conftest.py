"""
Repository 测试的共享 fixture。

每个测试使用独立的数据库会话，测试结束后回滚事务，
保证测试之间互不影响，不会在数据库中留下测试数据。
"""

import uuid
from collections.abc import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

# 用开发数据库（Phase 1a 暂不创建独立测试库）
# 每个测试回滚，不会污染数据
# NullPool：不缓存连接，避免测试间事件循环关闭导致连接失效
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
def sample_article_data() -> dict:
    """创建测试用的文章数据。"""
    return {
        "id": uuid.uuid4(),
        "title": "Test Article",
        "source": "curated",
        "difficulty": "medium",
        "topic": "technology",
        "word_count": 100,
        "content": "This is a test article content for testing purposes.",
        "is_published": True,
    }
