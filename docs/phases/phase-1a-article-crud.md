# Phase 1a: 文章模型与 CRUD

## 目标

建立文章（Article）的数据模型、数据访问层、服务层和 API 端点，实现完整的文章 CRUD 功能。本阶段**不涉及 LLM**，使用手动测试数据验证全链路可运行。阶段结束后可以手动创建、编辑、发布、浏览文章。

## 前置条件

- Phase 0（项目骨架）已完成
- PostgreSQL、Redis 服务可正常运行
- `backend/app/database.py`、`config.py`、`main.py` 已就绪
- Alembic 已初始化，`env.py` 已配置异步引擎

## 当前进度

**已完成**: Checkpoint 1a-1 ✅, Checkpoint 1a-2 ✅, Checkpoint 1a-3 ✅, Checkpoint 1a-4 ✅
**下一步**: Checkpoint 1a-5 — 前端文章页面（任务 1a.13, 1a.14）
**Git 分支**: `feature/P1a-4-cache-and-tests`

> 每个 checkpoint 完成后更新此节。新会话读此文件即可知道从哪继续。

## 检查点

### Checkpoint 1a-1: 文章数据模型
**任务**: 创建 models/article.py, Alembic 迁移, schemas/article.py
**Git 分支**: `feature/P1a-1-article-model`
**Git commit**: `feat(db): add article and segment models with schemas`

验证步骤：
1. `alembic upgrade head` — 迁移成功，创建了 articles 和 article_segments 表
2. `psql -U postgres -d ai_reading -c "\dt"` — 能看到新表
3. `pytest tests/test_models/` — 模型测试通过（如果有的话）
4. 重启 uvicorn → `curl /health` — 应用仍然正常

### Checkpoint 1a-2: Repository 层
**任务**: 创建 repositories/base.py, repositories/article_repo.py
**Git 分支**: `feature/P1a-2-repositories`
**Git commit**: `feat(db): add generic repository and article repository`

验证步骤：
1. `pytest tests/test_repositories/` — Repository CRUD 测试通过
2. 测试应覆盖：create, get, get_multi, get_by_difficulty, get_by_topic, pagination

### Checkpoint 1a-3: Service + API 端点
**任务**: 创建 services/article_service.py, api/v1/articles.py, api/v1/admin.py, api/v1/router.py
**Git 分支**: `feature/P1a-3-article-api`
**Git commit**: `feat(api): add article CRUD endpoints`

验证步骤：
1. `pytest tests/test_api/test_articles.py` — API 测试通过
2. 启动 uvicorn → `curl http://localhost:8000/docs` — 能看到 article 相关端点
3. `curl -X POST http://localhost:8000/api/v1/admin/articles -H "Content-Type: application/json" -H "X-Admin-Key: test" -d '{"title":"Test","source":"curated","difficulty":"easy","topic":"test","word_count":100,"content":"Test content"}'` — 创建文章成功，返回 201
4. `curl http://localhost:8000/api/v1/articles` — 返回文章列表，包含刚创建的文章
5. `curl http://localhost:8000/api/v1/articles/{id}` — 返回文章详情
6. `curl "http://localhost:8000/api/v1/articles?difficulty=easy"` — 过滤正常

### Checkpoint 1a-4: 缓存 + 文本工具 + 测试
**任务**: 添加 Redis 缓存, 文本处理工具, 完善 CRUD 测试
**Git 分支**: `feature/P1a-4-cache-and-tests`
**Git commit**: `feat(api): add Redis caching and text processing utils`

验证步骤：
1. `pytest` — 全部测试通过
2. 第一次 `curl /api/v1/articles/{id}` → 检查响应时间（首次查询，cache miss）
3. 第二次 `curl /api/v1/articles/{id}` → 响应更快（cache hit）
4. `redis-cli GET "article:{id}"` — 能看到缓存数据

### Checkpoint 1a-5: 前端文章页面
**任务**: 前端文章列表页, 文章详情页
**Git 分支**: `feature/P1a-5-frontend-articles`
**Git commit**: `feat(ui): add article list and detail pages`

验证步骤：
1. `npm run dev` → 浏览器打开首页 — 看到文章列表（卡片形式）
2. 点击文章卡片 — 跳转到文章详情页，显示段落内容
3. 文章列表页能看到：标题、难度标签、字数、主题
4. 文章详情页能看到：分段展示、预计阅读时间
5. F12 Network — API 调用成功，无 404/500

## 任务清单

| # | 任务 | 复杂度 | 状态 |
|---|---|---|---|
| 1a.1 | 创建 `models/article.py` — Article、ArticleSegment、DifficultyLevel 模型 | 中 | ✅ |
| 1a.2 | 创建 Alembic 迁移（articles + article_segments 表） | 低 | ✅ |
| 1a.3 | 创建 `schemas/article.py` — ArticleCreate, ArticleResponse, ArticleListResponse 等 Pydantic 模型 | 中 | ✅ |
| 1a.4 | 创建 `repositories/base.py` — 泛型异步 Repository：get(), get_multi(), create(), update(), delete(), count() | 中 | ✅ |
| 1a.5 | 创建 `repositories/article_repo.py` — 扩展基础 Repository：get_published(), get_by_difficulty(), get_by_topic(), search() | 中 | ✅ |
| 1a.6 | 创建 `services/article_service.py`（CRUD only，不含 LLM 生成逻辑） | 中 | ✅ |
| 1a.7 | 创建 `api/v1/articles.py` — 公开端点：文章列表、文章详情 | 中 | ✅ |
| 1a.8 | 创建 `api/v1/admin.py` — 管理 CRUD 端点（列表含草稿、更新状态、删除；不含 generate 端点） | 中 | ✅ |
| 1a.9 | 创建 `api/v1/router.py` — 聚合路由 | 低 | ✅ |
| 1a.10 | 创建 `utils/text_processing.py` — 分段、字数统计、阅读时间估算 | 中 | ✅ |
| 1a.11 | 添加 Redis 缓存（Cache-Aside 模式，缓存已发布文章，TTL 1 小时） | 中 | ✅ |
| 1a.12 | 编写测试 — Repository CRUD、API 端点（无 LLM mocking） | 高 | ✅ |
| 1a.13 | 前端：文章列表页 — HomeView，文章卡片展示（标题、难度、字数、主题） | 中 | ⬜ |
| 1a.14 | 前端：文章详情页 — ArticleView，段落展示、阅读时间 | 中 | ⬜ |

## API 端点

### 公开端点

```
GET /api/v1/articles
  认证：无
  查询参数：difficulty, topic, page(default 1), page_size(default 20, max 50)
  响应 200:
    {
      "items": [{ "id", "title", "difficulty", "topic", "cefr_level",
                   "word_count", "estimated_reading_time_minutes",
                   "published_at", "created_at" }],
      "total": 42, "page": 1, "page_size": 20, "pages": 3
    }

GET /api/v1/articles/{article_id}
  认证：无
  响应 200:
    {
      "id", "title", "difficulty", "topic", "cefr_level",
      "word_count", "estimated_reading_time_minutes",
      "segments": [{ "id", "segment_index", "segment_type", "content" }],
      "published_at"
    }
  响应 404: {"detail": "Article not found"}
```

### 管理 CRUD 端点（不含 generate）

```
POST /api/v1/admin/articles
  认证：Admin API Key (X-Admin-Key header)
  请求体：
    { "title": "string", "source": "curated",
      "difficulty": "medium", "topic": "technology",
      "cefr_level": "B2", "content": "全文...",
      "segments": [{ "segment_index": 0, "segment_type": "heading", "content": "..." }]
    }
  响应 201: 完整文章响应

GET /api/v1/admin/articles
  认证：Admin API Key
  查询参数：同公开 + include_unpublished=true
  响应 200: 分页文章列表（含草稿）

PATCH /api/v1/admin/articles/{article_id}
  认证：Admin API Key
  请求体：{ "is_published": true, "difficulty": "advanced" }
  响应 200: 完整文章响应

DELETE /api/v1/admin/articles/{article_id}
  认证：Admin API Key
  响应 204
```

## 数据模型变更

### articles 表

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | UUID | PK | |
| title | VARCHAR(500) | NOT NULL | 文章标题 |
| source | VARCHAR(50) | NOT NULL | 'ai_generated' / 'curated' / 'user_submitted' |
| difficulty | VARCHAR(20) | NOT NULL | easy/medium/hard |
| topic | VARCHAR(100) | | 分类标签 |
| word_count | INTEGER | | 预计算 |
| cefr_level | VARCHAR(4) | | A1-C2 |
| quality_score | FLOAT | CHECK (0-1) | Judge Agent 评分（本阶段为 NULL） |
| source_url | TEXT | | 原文链接（如精选） |
| generation_metadata | JSONB | | 使用的 prompt、模型、token 数（本阶段为 NULL） |
| content | TEXT | NOT NULL | 全文 |
| is_published | BOOLEAN | default false | 草稿/发布 |
| published_at | TIMESTAMPTZ | | |
| created_at | TIMESTAMPTZ | default now() | |
| updated_at | TIMESTAMPTZ | default now() | |

索引：`(difficulty)`, `(is_published, published_at)`, `(topic)`

### article_segments 表

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | UUID | PK | |
| article_id | UUID | FK articles(id) CASCADE | |
| segment_index | INTEGER | NOT NULL | 排序 |
| segment_type | VARCHAR(20) | NOT NULL | 'paragraph' / 'heading' |
| content | TEXT | NOT NULL | 段落文本 |

索引：`UNIQUE (article_id, segment_index)`

## 设计模式

1. **Repository 模式**：ArticleRepository 封装所有 SQL 查询，Service 层不直接写查询。泛型 `BaseRepository[T]` 提供通用 CRUD，`ArticleRepository` 继承并添加文章专属查询方法。
2. **Cache-Aside 模式**：读文章先查 Redis → 未命中查 DB → 写入 Redis（TTL 1 小时）；更新或删除文章时用 Redis DELETE 失效缓存，避免竞态条件。
3. **分层架构**：`API 层` → `Service 层` → `Repository 层` → `DB`，每层职责单一，便于独立测试和替换。

## 测试要求

| 层 | 测试内容 | 方式 |
|---|---|---|
| Repository | CRUD 操作、过滤、分页、排序 | 测试数据库，每个测试在事务中运行并回滚 |
| Service | 文章创建流程（含分段、字数计算）、发布/取消发布、缓存失效 | Mock Repository |
| API | 列表（分页、过滤）、详情（含 segments）、管理 CRUD、404 | httpx.AsyncClient + 测试数据库 |
| 前端 | 文章列表渲染、文章详情渲染、加载状态、空状态 | Vitest 组件测试 |

本阶段不需要 LLM mocking。使用手动构造的测试数据（硬编码文章内容）验证 CRUD 全链路。

### conftest.py 核心模式

```python
@pytest.fixture(scope="session")
async def engine():
    # 创建测试数据库引擎，运行迁移
    yield engine
    # 清理

@pytest.fixture
async def db_session(engine):
    # 每个测试在事务中运行，测试后回滚

@pytest.fixture
async def client(db_session):
    # 覆盖 get_db 依赖，返回 AsyncClient
```

## 陷阱

1. **Alembic 异步配置**：默认 `env.py` 是同步的，必须改写为 `run_async` 模式，Phase 0 已处理，此处创建迁移前确认可用
2. **文章分段一致性**：`content`（全文）和 `article_segments`（分段）必须保持一致，创建/更新时用 `text_processing.py` 的分段函数同步
3. **缓存失效时机**：更新文章（PATCH）和删除文章（DELETE）时都必须删除 Redis 缓存，用 `redis.delete(f"article:{article_id}")` 而非更新缓存
4. **is_published 过滤**：公开端点只返回 `is_published=True` 的文章，管理端点可看到所有文章，Repository 方法要区分
5. **Admin API Key 认证**：管理端点通过 `X-Admin-Key` header 认证，key 存在 `.env` 的 `ADMIN_API_KEY` 中，依赖注入校验
6. **word_count 预计算**：创建/更新文章时自动计算 `word_count` 和 `estimated_reading_time_minutes`，不在查询时动态计算
7. **Windows Docker 网络**：容器间用服务名（如 `postgres`、`redis`），容器访问宿主机用 `host.docker.internal`

## 验证标准

- `alembic upgrade head` 成功创建 articles 和 article_segments 表
- 通过 Admin API 手动创建一篇文章（含 segments），返回 201
- `GET /api/v1/articles` 返回已发布文章列表（分页正确）
- `GET /api/v1/articles/{id}` 返回文章详情（含 segments）
- `PATCH /admin/articles/{id}` 更新 `is_published` 为 true 后，公开列表可见
- `DELETE /admin/articles/{id}` 后返回 204，再次 GET 返回 404
- Redis 缓存命中：第二次请求文章详情时响应更快
- 所有测试通过：`pytest tests/ -v`
- 前端文章列表页能显示测试文章
- 前端文章详情页能显示段落内容和阅读时间
