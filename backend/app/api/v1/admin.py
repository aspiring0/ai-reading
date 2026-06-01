"""
管理端文章端点 — 通过 Admin API Key 认证，可操作草稿和已发布文章。

端点：
    POST   /api/v1/admin/articles          — 创建文章
    GET    /api/v1/admin/articles          — 文章列表（含草稿）
    PATCH  /api/v1/admin/articles/{id}     — 更新文章
    DELETE /api/v1/admin/articles/{id}     — 删除文章
"""

import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import get_db, get_redis
from app.schemas.article import ArticleCreate, ArticleListResponse, ArticleResponse, ArticleUpdate
from app.services.article_service import ArticleService

router = APIRouter(prefix="/admin/articles", tags=["admin"])


async def verify_admin_key(x_admin_key: str = Header(..., description="Admin API Key")) -> str:
    """校验 Admin API Key — 从请求头 X-Admin-Key 读取，和环境变量比对。"""
    if x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin API key")
    return x_admin_key


@router.post("", response_model=ArticleResponse, status_code=201)
async def create_article(
    body: ArticleCreate,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    _admin: str = Depends(verify_admin_key),
) -> ArticleResponse:
    """创建文章（Admin），自动分段和字数统计。"""
    service = ArticleService(db, redis)
    return await service.create_article(body)


@router.get("", response_model=ArticleListResponse)
async def list_all_articles(
    include_unpublished: bool = Query(True, description="是否包含草稿"),
    difficulty: str | None = Query(None, description="按难度过滤"),
    topic: str | None = Query(None, description="按主题过滤"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    _admin: str = Depends(verify_admin_key),
) -> ArticleListResponse:
    """获取所有文章（Admin），可选包含草稿。"""
    service = ArticleService(db, redis)
    return await service.get_all_articles(
        include_unpublished=include_unpublished,
        difficulty=difficulty,
        topic=topic,
        page=page,
        page_size=page_size,
    )


@router.patch("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: uuid.UUID,
    body: ArticleUpdate,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    _admin: str = Depends(verify_admin_key),
) -> ArticleResponse:
    """更新文章（Admin），更新后自动清除缓存。"""
    service = ArticleService(db, redis)
    return await service.update_article(article_id, body)


@router.delete("/{article_id}", status_code=204)
async def delete_article(
    article_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    _admin: str = Depends(verify_admin_key),
) -> None:
    """删除文章（Admin），删除后自动清除缓存。"""
    service = ArticleService(db, redis)
    await service.delete_article(article_id)
