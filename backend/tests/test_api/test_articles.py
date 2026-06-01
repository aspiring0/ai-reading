"""
文章 API 端点测试 — 验证公开端点和管理端点。

使用 httpx.AsyncClient + ASGITransport 直接调用 FastAPI，
通过 dependency_overrides 替换数据库 session。
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.repositories.article_repo import ArticleRepository

ADMIN_HEADERS = {"X-Admin-Key": "dev-admin-key"}


async def _seed_article(
    db_session: AsyncSession,
    *,
    title: str = "Test Article",
    difficulty: str = "easy",
    is_published: bool = True,
) -> Article:
    """辅助：直接往数据库插入一篇文章。"""
    repo = ArticleRepository(db_session)
    article = Article(
        id=uuid.uuid4(),
        title=title,
        source="curated",
        difficulty=difficulty,
        topic="technology",
        content="This is test content for the article.",
        is_published=is_published,
        word_count=8,
    )
    return await repo.create(article)


# --- 公开端点 ---


class TestPublicArticles:
    """GET /api/v1/articles, GET /api/v1/articles/{id}"""

    @pytest.mark.asyncio
    async def test_list_published_articles(self, client: AsyncClient, db_session: AsyncSession):
        """列表只返回已发布的文章。"""
        await _seed_article(db_session, title="Published", is_published=True)
        await _seed_article(db_session, title="Draft", is_published=False)

        resp = await client.get("/api/v1/articles")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Published"

    @pytest.mark.asyncio
    async def test_list_articles_pagination(self, client: AsyncClient, db_session: AsyncSession):
        """分页参数生效。"""
        for i in range(5):
            await _seed_article(db_session, title=f"Article {i}")

        resp = await client.get("/api/v1/articles?page=1&page_size=2")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["page_size"] == 2

    @pytest.mark.asyncio
    async def test_list_articles_filter_by_difficulty(self, client: AsyncClient, db_session: AsyncSession):
        """按难度过滤。"""
        await _seed_article(db_session, title="Easy", difficulty="easy")
        await _seed_article(db_session, title="Hard", difficulty="hard")

        resp = await client.get("/api/v1/articles?difficulty=easy")
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["difficulty"] == "easy"

    @pytest.mark.asyncio
    async def test_get_article_detail(self, client: AsyncClient, db_session: AsyncSession):
        """获取文章详情。"""
        article = await _seed_article(db_session)

        resp = await client.get(f"/api/v1/articles/{article.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Test Article"
        assert data["content"] == "This is test content for the article."
        assert "segments" in data

    @pytest.mark.asyncio
    async def test_get_article_not_found(self, client: AsyncClient):
        """查不存在的文章返回 404。"""
        fake_id = uuid.uuid4()
        resp = await client.get(f"/api/v1/articles/{fake_id}")
        assert resp.status_code == 404


# --- 管理端点 ---


class TestAdminArticles:
    """POST/GET/PATCH/DELETE /api/v1/admin/articles"""

    @pytest.mark.asyncio
    async def test_create_article(self, client: AsyncClient):
        """Admin 创建文章。"""
        resp = await client.post(
            "/api/v1/admin/articles",
            headers=ADMIN_HEADERS,
            json={
                "title": "New Article",
                "source": "curated",
                "difficulty": "medium",
                "topic": "science",
                "content": "This is a brand new article for testing.",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "New Article"
        assert data["difficulty"] == "medium"
        assert data["word_count"] == 8  # "This is a brand new article for testing." → 8 words

    @pytest.mark.asyncio
    async def test_create_article_with_segments(self, client: AsyncClient):
        """创建文章时同时传入段落数据。"""
        resp = await client.post(
            "/api/v1/admin/articles",
            headers=ADMIN_HEADERS,
            json={
                "title": "Article with Segments",
                "source": "ai_generated",
                "difficulty": "hard",
                "content": "Full content here.",
                "segments": [
                    {"segment_index": 0, "segment_type": "heading", "content": "Introduction"},
                    {"segment_index": 1, "segment_type": "paragraph", "content": "Body text here."},
                ],
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert len(data["segments"]) == 2
        assert data["segments"][0]["segment_type"] == "heading"

    @pytest.mark.asyncio
    async def test_create_article_without_admin_key(self, client: AsyncClient):
        """没有 Admin Key 创建文章返回 422（缺少必要 header）。"""
        resp = await client.post(
            "/api/v1/admin/articles",
            json={
                "title": "No Key",
                "source": "curated",
                "difficulty": "easy",
                "content": "Content.",
            },
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_article_wrong_admin_key(self, client: AsyncClient):
        """错误的 Admin Key 返回 403。"""
        resp = await client.post(
            "/api/v1/admin/articles",
            headers={"X-Admin-Key": "wrong-key"},
            json={
                "title": "Wrong Key",
                "source": "curated",
                "difficulty": "easy",
                "content": "Content.",
            },
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_list_all_articles_includes_drafts(self, client: AsyncClient, db_session: AsyncSession):
        """Admin 列表能看到草稿。"""
        await _seed_article(db_session, title="Published", is_published=True)
        await _seed_article(db_session, title="Draft", is_published=False)

        resp = await client.get("/api/v1/admin/articles?include_unpublished=true", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2

    @pytest.mark.asyncio
    async def test_update_article(self, client: AsyncClient, db_session: AsyncSession):
        """更新文章标题。"""
        article = await _seed_article(db_session)

        resp = await client.patch(
            f"/api/v1/admin/articles/{article.id}",
            headers=ADMIN_HEADERS,
            json={"title": "Updated Title"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Updated Title"

    @pytest.mark.asyncio
    async def test_publish_article(self, client: AsyncClient, db_session: AsyncSession):
        """发布草稿，published_at 应该被设置。"""
        article = await _seed_article(db_session, is_published=False)

        resp = await client.patch(
            f"/api/v1/admin/articles/{article.id}",
            headers=ADMIN_HEADERS,
            json={"is_published": True},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_published"] is True
        assert data["published_at"] is not None

    @pytest.mark.asyncio
    async def test_delete_article(self, client: AsyncClient, db_session: AsyncSession):
        """删除文章后查不到。"""
        article = await _seed_article(db_session)

        resp = await client.delete(
            f"/api/v1/admin/articles/{article.id}",
            headers=ADMIN_HEADERS,
        )
        assert resp.status_code == 204

        # 再查应该 404
        resp = await client.get(f"/api/v1/articles/{article.id}")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_nonexistent_article(self, client: AsyncClient):
        """删除不存在的文章返回 404。"""
        fake_id = uuid.uuid4()
        resp = await client.delete(
            f"/api/v1/admin/articles/{fake_id}",
            headers=ADMIN_HEADERS,
        )
        assert resp.status_code == 404
