"""
公开文章端点 — 不需要认证，只返回已发布的文章。

端点：
    GET /api/v1/articles          — 文章列表（分页、过滤）
    GET /api/v1/articles/{id}     — 文章详情（含段落）
"""

import uuid

from fastapi import APIRouter, Depends, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_redis
from app.schemas.article import ArticleListResponse, ArticleResponse
from app.services.article_service import ArticleService

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=ArticleListResponse)
async def list_articles(
    difficulty: str | None = Query(None, description="按难度过滤: easy/medium/hard"),
    topic: str | None = Query(None, description="按主题过滤"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=50, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> ArticleListResponse:
    """获取已发布文章列表。"""
    service = ArticleService(db, redis)
    return await service.get_published_articles(difficulty=difficulty, topic=topic, page=page, page_size=page_size)


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> ArticleResponse:
    """获取文章详情（含段落），带 Redis 缓存。"""
    service = ArticleService(db, redis)
    return await service.get_article_detail(article_id)
