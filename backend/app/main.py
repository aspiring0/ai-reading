"""
FastAPI 应用入口

这是整个后端应用的入口点，负责：
1. 创建 FastAPI 实例
2. 注册中间件（CORS 跨域）
3. 管理应用生命周期（启动时连接 Redis，关闭时断开）
4. 挂载 API 路由（/api/v1/）
5. 提供 /health 健康检查端点

启动方式：
    cd backend && uvicorn app.main:app --reload
    --reload 表示文件修改后自动重启（仅开发环境用）
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.v1.router import router as v1_router
from app.config import settings
from app.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理：yield 之前是启动逻辑，yield 之后是关闭逻辑。

    为什么用 lifespan 而不是 on_event：
        FastAPI 推荐用 lifespan 替代 @app.on_event，支持 async with 上下文管理。
    """
    # Startup: 连接 Redis（存储在 app.state 上，全局共享）
    app.state.redis = aioredis.from_url(settings.REDIS_URL)
    yield
    # Shutdown: 关闭 Redis 连接
    await app.state.redis.aclose()


# FastAPI 实例 — title 和 version 会显示在 /docs Swagger 文档页面
app = FastAPI(
    title="AI Reading",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS 中间件 — 允许前端（localhost:5173）跨域访问后端（localhost:8000）
# 浏览器的同源策略会阻止不同端口的请求，CORS 中间件解决这个问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载 v1 路由 — 所有 API 端点都在 /api/v1/ 路径下
# 例如：GET /api/v1/articles, POST /api/v1/auth/register
app.include_router(v1_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict:
    """健康检查端点，用于监控和运维。

    返回各组件的连接状态：
        - database: 执行 SELECT 1 验证数据库可达
        - redis: 执行 PING 验证缓存可达

    Docker 和负载均衡器通过此端点判断服务是否健康。
    """
    # Check database
    db_status = "connected"
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"

    # Check Redis
    redis_status = "connected"
    try:
        await app.state.redis.ping()
    except Exception:
        redis_status = "disconnected"

    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "database": db_status,
        "redis": redis_status,
    }
