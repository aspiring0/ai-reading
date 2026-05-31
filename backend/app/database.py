"""
数据库连接模块

负责创建异步数据库引擎和会话工厂。
所有数据库操作都通过 get_db() 获取会话，由 FastAPI 依赖注入管理生命周期。

架构中的位置：
    API 端点 → 调用 Service → 调用 Repository → 使用 get_db() 获取数据库会话

为什么用异步：
    FastAPI 是异步框架，数据库操作不能阻塞事件循环。
    asyncpg 是 PostgreSQL 的纯异步驱动，比 psycopg2 性能更好。
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

# 异步引擎 — 管理连接池，所有数据库操作共用
# echo=True 会在开发环境打印 SQL 语句，方便调试
# 连接串格式必须是 postgresql+asyncpg://user:pass@host:port/dbname
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENV == "development",
)

# 会话工厂 — 每次调用创建一个新的数据库会话
# expire_on_commit=False: commit 后对象属性仍然可用，避免懒加载报错
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖注入：为每个请求提供一个数据库会话。

    使用方式（在 API 端点中）：
        @router.get("/articles")
        async def list_articles(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Article))
            return result.scalars().all()

    生命周期：
        请求开始 → 创建会话 → 业务操作 → 成功则 commit / 失败则 rollback → 关闭会话
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
