"""
文章 Repository — 封装文章相关的所有数据库查询。

继承 BaseRepository 获得 get/create/update/delete/count 等基础操作，
额外添加文章专属的查询方法（按难度过滤、按主题过滤、搜索等）。
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.article import Article
from app.repositories.base import BaseRepository


class ArticleRepository(BaseRepository[Article]):
    """文章数据访问层 — Service 层通过此类操作 articles 表。"""

    def __init__(self, session: AsyncSession):
        super().__init__(Article, session)

    async def get_with_segments(self, article_id: uuid.UUID) -> Article | None:
        """查文章详情（含段落）— 用 selectinload 一次查完，避免 N+1。"""
        stmt = (
            select(Article)
            .where(Article.id == article_id)
            .options(selectinload(Article.segments))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_published(
        self,
        *,
        difficulty: str | None = None,
        topic: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Article]:
        """查已发布的文章列表，支持按难度/主题过滤 + 分页。"""
        stmt = select(Article).where(Article.is_published.is_(True))

        if difficulty:
            stmt = stmt.where(Article.difficulty == difficulty)
        if topic:
            stmt = stmt.where(Article.topic == topic)

        stmt = (
            stmt.order_by(Article.published_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_published(
        self,
        *,
        difficulty: str | None = None,
        topic: str | None = None,
    ) -> int:
        """统计已发布文章数，支持过滤条件。"""
        stmt = select(func.count()).select_from(Article).where(Article.is_published.is_(True))

        if difficulty:
            stmt = stmt.where(Article.difficulty == difficulty)
        if topic:
            stmt = stmt.where(Article.topic == topic)

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_all(
        self,
        *,
        include_unpublished: bool = False,
        difficulty: str | None = None,
        topic: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Article]:
        """查所有文章（管理用），可选包含草稿，支持过滤+分页。"""
        stmt = select(Article)

        if not include_unpublished:
            stmt = stmt.where(Article.is_published.is_(True))

        if difficulty:
            stmt = stmt.where(Article.difficulty == difficulty)
        if topic:
            stmt = stmt.where(Article.topic == topic)

        stmt = (
            stmt.order_by(Article.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_all(
        self,
        *,
        include_unpublished: bool = False,
        difficulty: str | None = None,
        topic: str | None = None,
    ) -> int:
        """统计所有文章数（管理用），可选包含草稿。"""
        stmt = select(func.count()).select_from(Article)

        if not include_unpublished:
            stmt = stmt.where(Article.is_published.is_(True))

        if difficulty:
            stmt = stmt.where(Article.difficulty == difficulty)
        if topic:
            stmt = stmt.where(Article.topic == topic)

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def search(
        self,
        query: str,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Article]:
        """按标题模糊搜索已发布的文章。"""
        stmt = (
            select(Article)
            .where(Article.is_published.is_(True), Article.title.ilike(f"%{query}%"))
            .order_by(Article.published_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
