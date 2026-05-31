"""
测试配置 — 提供共享的测试 fixture。

conftest.py 是 pytest 的特殊文件，里面的 fixture 所有测试文件都能用。
"""

from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """提供异步 HTTP 测试客户端。

    ASGITransport 让 httpx 直接调用 FastAPI 应用，不需要真正启动服务器。
    相当于模拟浏览器发请求，但跳过了网络层，速度更快。
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
