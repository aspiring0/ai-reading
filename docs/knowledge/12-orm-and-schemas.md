# ORM 模型与 Pydantic Schemas

## 什么是 ORM

ORM（Object-Relational Mapping）= 用 Python 类来操作数据库表。

不用 ORM（写 SQL）：
```python
cursor.execute("INSERT INTO articles (title, difficulty) VALUES ('Hello', 'easy')")
cursor.execute("SELECT * FROM articles WHERE difficulty = 'easy'")
```

用 ORM（写 Python）：
```python
article = Article(title="Hello", difficulty="easy")
session.add(article)
await session.commit()

result = await session.execute(select(Article).where(Article.difficulty == "easy"))
```

**好处**：
- 不用写 SQL 字符串（容易拼错）
- 类型安全（IDE 能提示 Article 有哪些字段）
- 换数据库不需要改代码（PostgreSQL → MySQL 只改连接串）

## models/ 和 schemas/ 为什么要分开

```python
# models/article.py — 数据库里的格式（什么都要存）
class Article(Base):
    id: UUID
    title: str
    content: str           # 全文，可能 5000 字
    is_published: bool
    quality_score: float   # AI 评分

# schemas/article.py — API 返回给前端的格式（按需给）
class ArticleListItem(BaseModel):
    id: UUID
    title: str
    difficulty: str
    word_count: int | None
    # 不返回 content（列表不需要 5000 字的全文）
    # 不返回 quality_score（用户不需要看到 AI 评分）
```

为什么不一样：
- 文章列表页只需要标题、难度、字数，不需要全文
- 内部字段（quality_score、generation_metadata）不应该暴露给用户
- 同一个数据库模型，不同接口可能返回不同的字段

类比：数据库是公司的全部档案，schema 是你给客户看的摘要。客户不需要看到内部评分。

## 我们定义了哪些模型（Phase 1a-1 后）

### articles 表
```
一篇文章的所有信息
┌──────────────┬───────────────┬──────────────┐
│ id (UUID)    │ title         │ source       │
│ difficulty   │ topic         │ word_count   │
│ cefr_level   │ quality_score │ source_url   │
│ content      │ is_published  │ published_at │
│ created_at   │ updated_at    │              │
└──────────────┴───────────────┴──────────────┘
```

### article_segments 表
```
一篇文章拆成的段落（用于分段式阅读）
┌──────────────┬───────────────┬──────────────┐
│ id (UUID)    │ article_id    │ segment_index│
│ segment_type │ content       │              │
└──────────────┴───────────────┴──────────────┘

一篇文章有多个段落，通过 article_id 关联
```

## relationship 是什么

```python
# Article 模型里：
segments: Mapped[list["ArticleSegment"]] = relationship(
    back_populates="article", cascade="all, delete-orphan"
)
```

这行代码的意思是：当我查一篇文章时，可以**自动带上它的所有段落**。

```python
article = await session.get(Article, article_id)
print(article.segments)  # 自动查到了所有段落，不需要再写 SQL
```

`cascade="all, delete-orphan"` 意思是：删掉文章时，它的段落也自动删除。

## mapped_column 和 Column 的区别

SQLAlchemy 2.0 用 `mapped_column`（新写法），旧版用 `Column`。我们用新写法：

```python
# 新写法（推荐，有类型提示）
title: Mapped[str] = mapped_column(String(500), nullable=False)

# 旧写法（不推荐）
title = Column(String(500), nullable=False)
```

新写法的好处：IDE 知道 `article.title` 是字符串，能自动补全。
