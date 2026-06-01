"""
Redis 缓存工具 — Cache-Aside 模式的封装。

Cache-Aside 模式流程：
    读：先查 Redis → 命中则直接返回 → 未命中则查数据库 → 写入 Redis
    写：更新/删除数据库 → 删除 Redis 缓存（不用更新缓存，避免竞态）

为什么用"删除"而不是"更新"缓存：
    并发场景下，"读-改-写缓存"可能产生旧数据覆盖新数据。
    直接删除缓存，下次读的时候自然从数据库拿最新的。
"""

import json
import logging

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

# 默认缓存时间：1 小时
DEFAULT_TTL = 3600


def _make_key(prefix: str, identifier: str) -> str:
    """生成缓存 key，如 article:uuid-xxx。"""
    return f"{prefix}:{identifier}"


async def get_cache(redis: aioredis.Redis, key: str) -> dict | None:
    """从 Redis 读取缓存，返回 dict 或 None（未命中）。"""
    try:
        data = await redis.get(key)
        if data is None:
            return None
        return json.loads(data)
    except Exception as e:
        logger.warning(f"Cache GET failed for key={key}: {e}")
        return None


async def set_cache(redis: aioredis.Redis, key: str, value: dict, ttl: int = DEFAULT_TTL) -> None:
    """写入 Redis 缓存，默认 1 小时过期。"""
    try:
        await redis.set(key, json.dumps(value, default=str), ex=ttl)
    except Exception as e:
        logger.warning(f"Cache SET failed for key={key}: {e}")


async def delete_cache(redis: aioredis.Redis, key: str) -> None:
    """删除 Redis 缓存。"""
    try:
        await redis.delete(key)
    except Exception as e:
        logger.warning(f"Cache DELETE failed for key={key}: {e}")


async def get_article_cache(redis: aioredis.Redis, article_id: str) -> dict | None:
    """快捷方法：读取文章缓存。"""
    return await get_cache(redis, _make_key("article", str(article_id)))


async def set_article_cache(redis: aioredis.Redis, article_id: str, data: dict) -> None:
    """快捷方法：写入文章缓存。"""
    await set_cache(redis, _make_key("article", str(article_id)), data)


async def delete_article_cache(redis: aioredis.Redis, article_id: str) -> None:
    """快捷方法：删除文章缓存。"""
    await delete_cache(redis, _make_key("article", str(article_id)))
