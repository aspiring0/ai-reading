"""
ArticleRepository 测试 — 验证文章相关的数据库查询。

覆盖：CRUD、按难度/主题过滤、分页、搜索。
"""

import uuid

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article, ArticleSegment
from app.repositories.article_repo import ArticleRepository


@pytest_asyncio.fixture
def repo(db_session: AsyncSession) -> ArticleRepository:
    """提供一个 ArticleRepository 实例。"""
    return ArticleRepository(db_session)


async def _create_article(
    repo: ArticleRepository,
    *,
    title: str = "Test Article",
    difficulty: str = "easy",
    topic: str | None = "technology",
    is_published: bool = True,
) -> Article:
    """辅助函数：快速创建一篇文章。"""
    article = Article(
        id=uuid.uuid4(),
        title=title,
        source="curated",
        difficulty=difficulty,
        topic=topic,
        content=f"Content of {title}",
        is_published=is_published,
    )
    return await repo.create(article)


# --- 基础 CRUD ---


class TestArticleCRUD:
    """测试基础增删改查操作。"""

    @pytest.mark.asyncio
    async def test_create_article(self, repo: ArticleRepository):
        """创建一篇文章并验证字段。"""
        article = await _create_article(repo)

        assert article.id is not None
        assert article.title == "Test Article"
        assert article.source == "curated"
        assert article.difficulty == "easy"
        assert article.is_published is True

    @pytest.mark.asyncio
    async def test_get_article_by_id(self, repo: ArticleRepository):
        """按 ID 查文章。"""
        created = await _create_article(repo)

        found = await repo.get(created.id)
        assert found is not None
        assert found.title == "Test Article"

    @pytest.mark.asyncio
    async def test_get_nonexistent_article(self, repo: ArticleRepository):
        """查不存在的 ID 返回 None。"""
        found = await repo.get(uuid.uuid4())
        assert found is None

    @pytest.mark.asyncio
    async def test_update_article(self, repo: ArticleRepository):
        """更新文章字段。"""
        article = await _create_article(repo)

        updated = await repo.update(article, {"title": "Updated Title", "difficulty": "hard"})
        assert updated.title == "Updated Title"
        assert updated.difficulty == "hard"

    @pytest.mark.asyncio
    async def test_delete_article(self, repo: ArticleRepository):
        """删除文章后查不到。"""
        article = await _create_article(repo)
        article_id = article.id

        await repo.delete(article)
        found = await repo.get(article_id)
        assert found is None

    @pytest.mark.asyncio
    async def test_count_articles(self, repo: ArticleRepository):
        """统计文章数量。"""
        await _create_article(repo, title="Article 1")
        await _create_article(repo, title="Article 2")

        count = await repo.count()
        assert count == 2


# --- 过滤和分页 ---


class TestArticleFiltering:
    """测试过滤和分页查询。"""

    @pytest.mark.asyncio
    async def test_get_published_only(self, repo: ArticleRepository):
        """只返回已发布的文章。"""
        await _create_article(repo, title="Published", is_published=True)
        await _create_article(repo, title="Draft", is_published=False)

        articles = await repo.get_published()
        assert len(articles) == 1
        assert articles[0].title == "Published"

    @pytest.mark.asyncio
    async def test_filter_by_difficulty(self, repo: ArticleRepository):
        """按难度过滤。"""
        await _create_article(repo, title="Easy", difficulty="easy")
        await _create_article(repo, title="Hard", difficulty="hard")

        articles = await repo.get_published(difficulty="easy")
        assert len(articles) == 1
        assert articles[0].difficulty == "easy"

    @pytest.mark.asyncio
    async def test_filter_by_topic(self, repo: ArticleRepository):
        """按主题过滤。"""
        await _create_article(repo, title="Tech", topic="technology")
        await _create_article(repo, title="Science", topic="science")

        articles = await repo.get_published(topic="technology")
        assert len(articles) == 1
        assert articles[0].topic == "technology"

    @pytest.mark.asyncio
    async def test_count_published_with_filter(self, repo: ArticleRepository):
        """带过滤条件的统计。"""
        await _create_article(repo, title="Easy Tech", difficulty="easy", topic="technology")
        await _create_article(repo, title="Hard Tech", difficulty="hard", topic="technology")
        await _create_article(repo, title="Easy Science", difficulty="easy", topic="science")

        count_all = await repo.count_published()
        assert count_all == 3

        count_easy = await repo.count_published(difficulty="easy")
        assert count_easy == 2

        count_tech = await repo.count_published(topic="technology")
        assert count_tech == 2

    @pytest.mark.asyncio
    async def test_pagination(self, repo: ArticleRepository):
        """分页查询。"""
        for i in range(5):
            await _create_article(repo, title=f"Article {i}")

        page1 = await repo.get_published(offset=0, limit=2)
        page2 = await repo.get_published(offset=2, limit=2)

        assert len(page1) == 2
        assert len(page2) == 2

    @pytest.mark.asyncio
    async def test_get_all_includes_unpublished(self, repo: ArticleRepository):
        """管理查询可包含草稿。"""
        await _create_article(repo, title="Published", is_published=True)
        await _create_article(repo, title="Draft", is_published=False)

        all_with_drafts = await repo.get_all(include_unpublished=True)
        published_only = await repo.get_all(include_unpublished=False)

        assert len(all_with_drafts) == 2
        assert len(published_only) == 1


# --- 搜索 ---


class TestArticleSearch:
    """测试标题搜索。"""

    @pytest.mark.asyncio
    async def test_search_by_title(self, repo: ArticleRepository):
        """按标题模糊搜索。"""
        await _create_article(repo, title="Climate Change Effects")
        await _create_article(repo, title="AI in Healthcare")

        results = await repo.search("Climate")
        assert len(results) == 1
        assert "Climate" in results[0].title

    @pytest.mark.asyncio
    async def test_search_case_insensitive(self, repo: ArticleRepository):
        """搜索不区分大小写。"""
        await _create_article(repo, title="Python Programming")

        results = await repo.search("python")
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_search_no_results(self, repo: ArticleRepository):
        """搜索无结果返回空列表。"""
        await _create_article(repo, title="Existing Article")

        results = await repo.search("nonexistent")
        assert results == []


# --- 文章详情（含段落）---


class TestArticleWithSegments:
    """测试文章详情查询（含关联段落）。"""

    @pytest.mark.asyncio
    async def test_get_with_segments(self, repo: ArticleRepository, db_session: AsyncSession):
        """查文章详情时自动带出段落。"""
        article = await _create_article(repo)

        segment = ArticleSegment(
            id=uuid.uuid4(),
            article_id=article.id,
            segment_index=0,
            segment_type="paragraph",
            content="First paragraph.",
        )
        db_session.add(segment)
        await db_session.flush()

        found = await repo.get_with_segments(article.id)
        assert found is not None
        assert len(found.segments) == 1
        assert found.segments[0].content == "First paragraph."

    @pytest.mark.asyncio
    async def test_get_with_segments_not_found(self, repo: ArticleRepository):
        """查不存在的文章返回 None。"""
        found = await repo.get_with_segments(uuid.uuid4())
        assert found is None
