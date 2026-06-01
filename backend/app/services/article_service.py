"""
文章 Service — 编排文章相关的业务逻辑。

Service 层的职责：
    1. 调用 Repository 操作数据库
    2. 处理业务规则（字数计算、发布状态切换等）
    3. 转换数据格式（ORM 模型 → Pydantic 响应）
    4. 管理 Redis 缓存（Cache-Aside 模式）
    5. 抛出业务异常（让 API 层统一处理）

不在这里做的事：
    - 不写 SQL（通过 Repository）
    - 不直接处理 HTTP 请求（由 API 层负责）
"""

import math
import uuid
from datetime import UTC, datetime

import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundException
from app.models.article import Article, ArticleSegment
from app.repositories.article_repo import ArticleRepository
from app.schemas.article import (
    ArticleCreate,
    ArticleListItem,
    ArticleListResponse,
    ArticleResponse,
    ArticleUpdate,
)
from app.utils.cache import (
    delete_article_cache,
    get_article_cache,
    set_article_cache,
)
from app.utils.text_processing import count_words, estimate_reading_time, split_into_paragraphs


class ArticleService:
    """文章业务逻辑 — API 层调用这里，这里调用 Repository。"""

    def __init__(self, session: AsyncSession, redis: aioredis.Redis | None = None):
        self.repo = ArticleRepository(session)
        self.session = session
        self.redis = redis

    def _to_response(self, article: Article) -> ArticleResponse:
        """ORM 模型 → Pydantic 响应，附带阅读时间。"""
        resp = ArticleResponse.model_validate(article)
        resp.estimated_reading_time_minutes = estimate_reading_time(resp.word_count or 0)
        return resp

    async def get_published_articles(
        self,
        *,
        difficulty: str | None = None,
        topic: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ArticleListResponse:
        """获取已发布文章列表（带过滤和分页）。"""
        offset = (page - 1) * page_size
        total = await self.repo.count_published(difficulty=difficulty, topic=topic)
        articles = await self.repo.get_published(difficulty=difficulty, topic=topic, offset=offset, limit=page_size)

        return ArticleListResponse(
            items=[ArticleListItem.model_validate(a) for a in articles],
            total=total,
            page=page,
            page_size=page_size,
            pages=math.ceil(total / page_size) if total > 0 else 0,
        )

    async def get_article_detail(self, article_id: uuid.UUID) -> ArticleResponse:
        """获取文章详情（含段落），先查缓存。

        Cache-Aside 模式：
            1. 查 Redis 缓存
            2. 命中 → 直接返回
            3. 未命中 → 查数据库 → 写入缓存 → 返回
        """
        # 尝试从缓存读取
        if self.redis:
            cached = await get_article_cache(self.redis, str(article_id))
            if cached:
                return ArticleResponse(**cached)

        # 缓存未命中，查数据库
        article = await self.repo.get_with_segments(article_id)
        if not article:
            raise NotFoundException("Article not found")

        resp = self._to_response(article)

        # 写入缓存
        if self.redis:
            await set_article_cache(self.redis, str(article_id), resp.model_dump(mode="json"))

        return resp

    async def create_article(self, data: ArticleCreate) -> ArticleResponse:
        """创建文章（Admin 用），自动计算字数，处理段落。"""
        word_count = count_words(data.content)

        article = Article(
            title=data.title,
            source=data.source,
            difficulty=data.difficulty,
            topic=data.topic,
            cefr_level=data.cefr_level,
            content=data.content,
            word_count=word_count,
        )
        article = await self.repo.create(article)

        # 如果传入了段落数据，直接使用；否则自动分段
        if data.segments:
            for seg in data.segments:
                segment = ArticleSegment(
                    article_id=article.id,
                    segment_index=seg.segment_index,
                    segment_type=seg.segment_type,
                    content=seg.content,
                )
                self.session.add(segment)
        else:
            # 自动从 content 生成段落
            paragraphs = split_into_paragraphs(data.content)
            for para in paragraphs:
                segment = ArticleSegment(
                    article_id=article.id,
                    **para,
                )
                self.session.add(segment)

        await self.session.flush()
        # 统一用 get_with_segments 重新加载（eager load segments，避免懒加载报错）
        article = await self.repo.get_with_segments(article.id)
        return self._to_response(article)

    async def update_article(self, article_id: uuid.UUID, data: ArticleUpdate) -> ArticleResponse:
        """更新文章（Admin 用），只更新传入的字段。"""
        article = await self.repo.get(article_id)
        if not article:
            raise NotFoundException("Article not found")

        # 构建更新字典（只包含非 None 的字段）
        update_data = data.model_dump(exclude_none=True)

        # 如果更新了 content，重新计算字数
        if "content" in update_data:
            update_data["word_count"] = count_words(update_data["content"])

        # 如果切换为发布状态，设置发布时间
        if update_data.get("is_published") is True and not article.is_published:
            update_data["published_at"] = datetime.now(UTC)

        article = await self.repo.update(article, update_data)

        # 清除缓存（更新后旧数据无效）
        if self.redis:
            await delete_article_cache(self.redis, str(article_id))

        # 重新加载含 segments
        article = await self.repo.get_with_segments(article.id)
        return self._to_response(article)

    async def delete_article(self, article_id: uuid.UUID) -> None:
        """删除文章（Admin 用）。"""
        article = await self.repo.get(article_id)
        if not article:
            raise NotFoundException("Article not found")
        await self.repo.delete(article)

        # 清除缓存
        if self.redis:
            await delete_article_cache(self.redis, str(article_id))

    async def get_all_articles(
        self,
        *,
        include_unpublished: bool = False,
        difficulty: str | None = None,
        topic: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ArticleListResponse:
        """获取所有文章（Admin 用），可选包含草稿。"""
        offset = (page - 1) * page_size
        total = await self.repo.count_all(include_unpublished=include_unpublished, difficulty=difficulty, topic=topic)
        articles = await self.repo.get_all(
            include_unpublished=include_unpublished,
            difficulty=difficulty,
            topic=topic,
            offset=offset,
            limit=page_size,
        )

        return ArticleListResponse(
            items=[ArticleListItem.model_validate(a) for a in articles],
            total=total,
            page=page,
            page_size=page_size,
            pages=math.ceil(total / page_size) if total > 0 else 0,
        )
