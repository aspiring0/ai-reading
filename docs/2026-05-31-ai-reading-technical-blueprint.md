# AI 英语阅读产品 — 完整技术蓝图与开发计划

## Context

用户是一名 Python 后端开发者，没有完整全栈项目经验，希望开发一个多智能体 AIGC 产品，兼顾**学习全流程**、**作品集展示**、**商业化潜力**。产品方向已确定为 **AI 英语阅读学习应用**（基于用户已有的详细产品方案）。核心担忧是项目过程中混乱、步骤遗漏、无法完成，因此需要一份**每一步都可以直接照做的技术蓝图**。

**产品方案原文**：`D:\A_my\笔记\产品思路\英文文章阅读器.md`

**MVP 范围**（4 个核心功能）：
1. 首页每日文章推荐
2. 分段式阅读 + 四层折叠辅助
3. 用户个人语料库（词汇/短语/语义块/句子/语法点）
4. 轻量理解反馈（1-3 道题）

---

## 一、总体架构

```
+------------------------------------------------------------------+
|                         客户端层                                    |
|  Vue 3 + Vite + TypeScript + Pinia + Vue Router + TailwindCSS    |
+--------------------------------+---------------------------------+
                                 |
                           HTTPS / REST
                                 |
+--------------------------------v---------------------------------+
|                      Nginx（反向代理 + 静态文件）                    |
+--------------------------------+---------------------------------+
                                 |
+--------------------------------v---------------------------------+
|                     FastAPI 应用服务器                               |
|  +------------------------------------------------------------+  |
|  |  中间件：CORS | Auth(JWT) | 限流 | 请求日志                   |  |
|  +------------------------------------------------------------+  |
|  |  API 路由层           |  后台任务（内容生成、SRS调度）           |  |
|  +----------+-----------+----------+----------------------------+  |
|  | Service 层（业务逻辑）  |  Agents 层（LLM 智能体）              |  |
|  +----------+-----------+----------+----------------------------+  |
|  | Repository 层（数据访问）                                      |  |
|  +----------+-----------+----------+----------------------------+  |
+--------------+------+---------------+----------------+------------+
               |               |                |
  +------------v---+ +---------v------+ +-------v--------+
  |  PostgreSQL    | |  Redis         | | LLM API        |
  |  (主数据库)     | | (缓存/队列)     | | (OpenAI兼容)    |
  +----------------+ +----------------+ +----------------+
```

### 技术栈选型与理由

| 层 | 技术 | 理由 |
|---|---|---|
| 后端 | Python 3.11+ / FastAPI | 你熟悉的语言，原生 async，自动 OpenAPI 文档，Pydantic 类型校验 |
| ORM | SQLAlchemy 2.0 (async) + asyncpg | 成熟、文档完善、异步原生 |
| 迁移 | Alembic | SQLAlchemy 标准配套 |
| 数据库 | PostgreSQL 16 | JSONB 支持灵活内容存储、全文搜索、成熟免费 |
| 缓存/队列 | Redis 7 | 缓存文章内容、后台任务队列、限流 |
| 前端 | Vue 3 (Composition API) + TypeScript | 学习曲线比 React 平缓，单文件组件直观，Pinia 比 Redux 简单，官方文档优秀 |
| 构建 | Vite | 快速启动，Vue 原生支持 |
| 样式 | TailwindCSS | 原子化 CSS，快速原型，不需要 CSS 架构决策 |
| 状态管理 | Pinia | Vue 官方推荐，TypeScript-first |
| LLM | OpenAI SDK (直连) | 不用 LangChain，减少依赖膨胀，直接 SDK 调用更可调试 |
| 间隔重复 | fsrs Python 库 | 成熟的 SRS 算法实现，不要自己造轮子 |
| 容器 | Docker + Docker Compose | 本地开发环境统一，部署一致 |
| CI/CD | GitHub Actions | 公开仓库免费 |
| 代码规范 | 后端 ruff / 前端 eslint + prettier | 统一代码风格 |

---

## 二、项目目录结构

```
ai-reading/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # PR 触发：lint + test
│       └── deploy.yml                # 合并 main 触发部署
├── backend/
│   ├── alembic/
│   │   └── versions/                 # 迁移文件
│   ├── alembic.ini
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI 应用创建、中间件注册
│   │   ├── config.py                 # pydantic-settings 配置类
│   │   ├── database.py              # DB 引擎、会话工厂
│   │   ├── dependencies.py          # 共享依赖（get_db, get_current_user）
│   │   ├── exceptions.py            # 自定义异常层级
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── router.py         # 聚合所有 v1 路由
│   │   │       ├── auth.py           # 认证端点
│   │   │       ├── articles.py       # 文章端点
│   │   │       ├── reading.py        # 阅读会话端点
│   │   │       ├── corpus.py         # 语料库端点
│   │   │       ├── feedback.py       # 理解题端点
│   │   │       ├── dashboard.py      # 仪表盘端点
│   │   │       └── admin.py          # 管理端点
│   │   ├── models/                   # SQLAlchemy ORM 模型
│   │   │   ├── user.py
│   │   │   ├── article.py
│   │   │   ├── reading.py
│   │   │   ├── corpus.py
│   │   │   └── feedback.py
│   │   ├── schemas/                  # Pydantic 请求/响应模型
│   │   │   ├── auth.py
│   │   │   ├── article.py
│   │   │   ├── reading.py
│   │   │   ├── corpus.py
│   │   │   └── feedback.py
│   │   ├── services/                 # 业务逻辑层
│   │   │   ├── auth_service.py
│   │   │   ├── article_service.py
│   │   │   ├── reading_service.py
│   │   │   ├── corpus_service.py
│   │   │   ├── feedback_service.py
│   │   │   ├── srs_service.py
│   │   │   └── recommendation_service.py
│   │   ├── agents/                   # LLM 智能体实现
│   │   │   ├── base.py              # 基础 Agent 类
│   │   │   ├── content_generator.py  # 内容生成 Agent
│   │   │   ├── content_judge.py      # 质量评判 Agent
│   │   │   ├── reading_assistant.py  # 阅读辅助 Agent
│   │   │   ├── grammar_analyzer.py   # 语法分析 Agent
│   │   │   └── question_generator.py # 出题 Agent
│   │   ├── repositories/             # 数据访问层
│   │   │   ├── base.py              # 泛型 Repository
│   │   │   ├── user_repo.py
│   │   │   ├── article_repo.py
│   │   │   ├── reading_repo.py
│   │   │   ├── corpus_repo.py
│   │   │   └── feedback_repo.py
│   │   └── utils/
│   │       ├── security.py          # JWT、密码哈希
│   │       ├── cache.py             # Redis 缓存辅助
│   │       └── text_processing.py   # 文本分段、字数统计
│   ├── tests/
│   │   ├── conftest.py              # 共享 fixture（测试 DB、客户端）
│   │   ├── test_api/
│   │   ├── test_services/
│   │   └── test_agents/
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── router/index.ts
│   │   ├── stores/                   # Pinia 状态管理
│   │   ├── api/                      # API 调用层
│   │   ├── views/                    # 页面级组件
│   │   ├── components/              # 可复用组件
│   │   ├── composables/             # Vue 组合式函数
│   │   ├── types/                   # TypeScript 类型定义
│   │   └── assets/styles/
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml               # 本地开发环境
├── docker-compose.prod.yml          # 生产环境
├── .env.example
├── .gitignore
├── Makefile                         # 便捷命令
└── README.md
```

**关键设计决策**：
- **为什么分 Repository 层**：将数据访问与业务逻辑解耦，Service 层不写 SQL，测试时 mock Repository 即可
- **为什么 schemas/ 与 models/ 分开**：SQLAlchemy 模型定义数据库形状，Pydantic 模型定义 API 形状，二者经常不同（如响应排除密码哈希）
- **为什么 agents/ 与 services/ 分开**：Agent 是 LLM 特定逻辑（提示词工程、输出解析），Service 编排 Agent 和 Repository，分开可独立测试

---

## 三、完整数据库设计

### ER 关系概览

```
users ──< corpus_entries ──< review_log
  │
  ├──< user_preferences
  │
  ├──< reading_sessions ──< lookup_events
  │                           │
articles ──< article_segments │
  │                           │
  └──< quiz_questions ──< quiz_responses
                          (关联 reading_sessions)
```

### 核心表结构

#### users（Phase 3）

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | UUID | PK, default uuid_generate_v4() | |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 登录标识 |
| password_hash | TEXT | NOT NULL | bcrypt 哈希 |
| display_name | VARCHAR(100) | | 显示名 |
| level | VARCHAR(20) | NOT NULL, default 'intermediate' | beginner/intermediate/advanced |
| target_score | VARCHAR(20) | | 如 "IELTS 7.0" |
| native_language | VARCHAR(10) | default 'zh' | 翻译方向 |
| daily_goal_minutes | INTEGER | default 15 | 每日阅读目标 |
| onboarding_complete | BOOLEAN | default false | 是否完成问卷 |
| created_at | TIMESTAMPTZ | default now() | |
| updated_at | TIMESTAMPTZ | default now() | 触发器自动更新 |

索引：`UNIQUE INDEX idx_users_email ON (email)`

#### articles（Phase 1）

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | UUID | PK | |
| title | VARCHAR(500) | NOT NULL | 文章标题 |
| source | VARCHAR(50) | NOT NULL | 'ai_generated' / 'curated' / 'user_submitted' |
| difficulty | VARCHAR(20) | NOT NULL | easy/medium/hard |
| topic | VARCHAR(100) | | 分类标签 |
| word_count | INTEGER | | 预计算 |
| cefr_level | VARCHAR(4) | | A1-C2 |
| quality_score | FLOAT | CHECK (0-1) | Judge Agent 评分 |
| source_url | TEXT | | 原文链接（如精选） |
| generation_metadata | JSONB | | 使用的 prompt、模型、token 数 |
| content | TEXT | NOT NULL | 全文 |
| is_published | BOOLEAN | default false | 草稿/发布 |
| published_at | TIMESTAMPTZ | | |
| created_at | TIMESTAMPTZ | default now() | |
| updated_at | TIMESTAMPTZ | default now() | |

索引：`(difficulty)`, `(is_published, published_at)`, `(topic)`

#### article_segments（Phase 1）

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | UUID | PK | |
| article_id | UUID | FK articles(id) CASCADE | |
| segment_index | INTEGER | NOT NULL | 排序 |
| segment_type | VARCHAR(20) | NOT NULL | 'paragraph' / 'heading' |
| content | TEXT | NOT NULL | 段落文本 |

索引：`UNIQUE (article_id, segment_index)`

#### reading_sessions（Phase 2）

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | UUID | PK | |
| user_id | UUID | FK users(id) (Phase 3 加) | |
| article_id | UUID | FK articles(id) | |
| started_at | TIMESTAMPTZ | NOT NULL | |
| ended_at | TIMESTAMPTZ | | |
| total_duration_seconds | INTEGER | | 活跃阅读时间 |
| words_looked_up | INTEGER | default 0 | 查词次数 |
| segments_read | INTEGER | default 0 | |
| completion_percentage | FLOAT | default 0 | |
| created_at | TIMESTAMPTZ | default now() | |

索引：`(user_id, started_at)`, `(user_id, article_id)`

#### corpus_entries（Phase 3）

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | UUID | PK | |
| user_id | UUID | FK users(id) CASCADE | |
| entry_type | VARCHAR(20) | NOT NULL | 'word'/'phrase'/'chunk'/'sentence'/'grammar_point' |
| content | TEXT | NOT NULL | 词条内容 |
| context | TEXT | | 原文上下文 |
| context_source_id | UUID | FK articles(id) NULL | 来源文章 |
| context_segment_index | INTEGER | | 来源段落 |
| translation | TEXT | | 母语翻译 |
| definition | TEXT | | 英文释义 |
| cefr_level | VARCHAR(4) | | |
| srs_data | JSONB | default '{}' | FSRS 状态 |
| next_review | TIMESTAMPTZ | | 下次复习时间 |
| review_count | INTEGER | default 0 | |
| created_at | TIMESTAMPTZ | default now() | |
| updated_at | TIMESTAMPTZ | default now() | |

索引：`(user_id)`, `(user_id, entry_type)`, `(user_id, next_review) WHERE next_review IS NOT NULL`, `(user_id, content)` 用于去重

#### review_log（Phase 3）

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | UUID | PK | |
| corpus_entry_id | UUID | FK corpus_entries(id) CASCADE | |
| rating | SMALLINT | NOT NULL, CHECK (1-4) | 1=Again, 2=Hard, 3=Good, 4=Easy |
| state | JSONB | | FSRS 状态快照 |
| reviewed_at | TIMESTAMPTZ | default now() | |

#### quiz_questions（Phase 4）

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | UUID | PK | |
| article_id | UUID | FK articles(id) | |
| question_text | TEXT | NOT NULL | |
| question_type | VARCHAR(20) | NOT NULL | 'multiple_choice'/'true_false'/'short_answer' |
| options | JSONB | | 选择题选项 |
| correct_answer | TEXT | NOT NULL | |
| explanation | TEXT | | 解析 |
| difficulty | VARCHAR(20) | | |
| created_at | TIMESTAMPTZ | default now() | |

#### quiz_responses（Phase 4）

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | UUID | PK | |
| user_id | UUID | FK users(id) | |
| question_id | UUID | FK quiz_questions(id) | |
| session_id | UUID | FK reading_sessions(id) | |
| user_answer | TEXT | NOT NULL | |
| is_correct | BOOLEAN | | |
| time_taken_seconds | INTEGER | | |
| created_at | TIMESTAMPTZ | default now() | |

---

## 四、分期开发计划

### 分期依赖关系

```
Phase 0（项目骨架）─ 2周
  │
  ▼
Phase 1（内容管线）─ 3周
  │
  ▼
Phase 2（阅读核心）─ 3周
  │
  ▼
Phase 3（用户系统与语料库）─ 3周
  │
  ▼
Phase 4（理解反馈与MVP完善）─ 2周
  │
  ▼
MVP 完成 ✓
```

> 时间按兼职（晚上/周末）估算。全职约 6-7 周。每个 Phase 结束都是**可运行状态**。

---

### Phase 0：项目骨架

**目标**：可运行的项目骨架，包含数据库、CI/CD、开发环境、一个健康检查端点。

#### 任务拆分

| # | 任务 | 复杂度 | 详细说明 |
|---|---|---|---|
| 0.1 | 初始化 git 仓库 | 低 | `git init`，创建 `.gitignore`（Python + Node + IDE 模板） |
| 0.2 | 创建目录结构 | 低 | 按上面的结构创建空目录和 `__init__.py` |
| 0.3 | 创建 pyproject.toml | 低 | 核心依赖：fastapi, uvicorn, sqlalchemy[asyncio], asyncpg, alembic, pydantic-settings, redis, openai, python-jose[cryptography], passlib[bcrypt], httpx, ruff |
| 0.4 | 创建 docker-compose.yml | 中 | 服务：postgres (5432)、redis (6379)，带 volume 持久化和健康检查 |
| 0.5 | 创建 config.py | 中 | pydantic-settings BaseSettings，字段：DATABASE_URL, REDIS_URL, SECRET_KEY, OPENAI_API_KEY, OPENAI_BASE_URL, CORS_ORIGINS, ENV |
| 0.6 | 创建 database.py | 中 | 异步引擎、async sessionmaker、`get_db()` 依赖。连接串必须用 `postgresql+asyncpg://` |
| 0.7 | 创建 main.py | 中 | FastAPI 实例，注册 CORS 中间件，lifespan 处理 Redis 连接/断开，挂载 v1 路由，添加 `/health` 端点 |
| 0.8 | 初始化 Alembic | 中 | `alembic init alembic`，配置 `env.py` 使用异步引擎并导入模型 |
| 0.9 | 创建初始迁移 | 低 | `alembic revision --autogenerate -m "initial"` |
| 0.10 | 创建 Makefile | 低 | 目标：`dev`(docker-compose up), `migrate`, `test`, `lint`, `format` |
| 0.11 | 创建 .env.example | 低 | 文档化所有必需的环境变量 |
| 0.12 | 创建 exceptions.py | 低 | 异常层级：AppException → NotFoundException / ValidationException / ExternalServiceException |
| 0.13 | 创建 dependencies.py | 低 | 共享依赖：get_db(), get_redis(), get_current_user()（暂为桩） |
| 0.14 | 初始化前端 | 低 | `npm create vue@latest`，选 TypeScript + Pinia + Vue Router |
| 0.15 | 安装 TailwindCSS | 低 | `npm install -D tailwindcss @tailwindcss/vite`，配置 |
| 0.16 | 创建前端 API 客户端骨架 | 中 | Axios 实例，带 auth token 拦截器和错误处理 |
| 0.17 | 创建基础布局和路由 | 中 | AppHeader、HomeView（占位）、3 个占位路由 |
| 0.18 | 配置 GitHub Actions CI | 中 | PR 触发：后端 lint (ruff) + test (pytest)，前端 lint + build |
| 0.19 | 配置代码规范工具 | 低 | 后端：ruff（在 pyproject.toml），前端：eslint + prettier |
| 0.20 | 编写第一个测试 | 低 | 测试 `GET /health` 返回 200，用 httpx.AsyncClient + ASGITransport |
| 0.21 | 创建 Dockerfile | 中 | 后端和前端各一个，多阶段构建 |
| 0.22 | 全栈启动验证 | 低 | `docker-compose up` 端到端冒烟测试 |

#### API 端点（Phase 0）

```
GET /health
  认证：无
  响应 200:
    {
      "status": "ok",
      "version": "0.1.0",
      "database": "connected" | "disconnected",
      "redis": "connected" | "disconnected"
    }
```

#### 测试策略

| 类型 | 工具 | 测试内容 |
|---|---|---|
| 单元 | pytest + pytest-asyncio | 配置加载、异常类 |
| 集成 | httpx.AsyncClient | 健康检查端点（用测试数据库） |

conftest.py 核心模式：
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

#### Git 工作流（贯穿全程）

**分支策略**：GitHub Flow
- `main` — 生产代码，受保护，合并需要 CI 通过
- `develop` — 集成分支，所有功能分支先合并到这里
- `feature/P0-xxx-description` — 功能分支，如 `feature/P0-setup-database`

**提交规范**：Conventional Commits
- `feat(scope): 描述` — 新功能
- `fix(scope): 描述` — 修复
- `chore(scope): 描述` — 构建、CI、工具
- `refactor(scope): 描述` — 重构
- `test(scope): 描述` — 测试
- scope 示例：api, db, agents, ui, ci

**PR 流程**：
1. 从 develop 创建功能分支
2. 提交代码
3. 推送并创建 PR 到 develop
4. CI 必须通过（lint + test）
5. 自查 diff 后合并

#### 常见陷阱

1. **忘记安装异步数据库驱动**：必须用 `asyncpg`（不是 `psycopg2`），连接串用 `postgresql+asyncpg://`
2. **Alembic 异步配置**：默认 `env.py` 是同步的，必须改写为 `run_async` 模式
3. **Windows Docker 网络**：容器间用服务名（如 `postgres`、`redis`），容器访问宿主机用 `host.docker.internal`
4. **环境变量加载**：`pydantic-settings` 自动读 `.env`，但要确保工作目录正确，建议显式指定 `env_file`
5. **开发环境 CORS**：前端在 5173，后端在 8000，CORS 必须允许 `http://localhost:5173`

---

### Phase 1：内容管线

**目标**：通过 LLM Agent 生成英语文章、评估质量、存储并提供管理 API。Phase 1 结束后可以生成和浏览文章（无用户系统）。

#### 任务拆分

| # | 任务 | 复杂度 | 详细说明 |
|---|---|---|---|
| 1.1 | 创建 models/article.py | 中 | Article、ArticleSegment、DifficultyLevel 模型 |
| 1.2 | 创建 Alembic 迁移 | 低 | |
| 1.3 | 创建 schemas/article.py | 中 | ArticleCreate, ArticleResponse, ArticleListResponse, ContentGenerationRequest, ContentGenerationResponse |
| 1.4 | 创建 repositories/base.py | 中 | 泛型异步 Repository：get(), get_multi(), create(), update(), delete(), count() |
| 1.5 | 创建 repositories/article_repo.py | 中 | 扩展基础 Repository：get_published(), get_by_difficulty(), get_by_topic(), search() |
| 1.6 | 创建 agents/base.py | 中 | BaseAgent 类：system_prompt 管理、LLM 调用、JSON 解析、重试逻辑、错误处理 |
| 1.7 | 创建 agents/content_generator.py | 高 | 内容生成 Agent，返回结构化 JSON：{title, segments, word_count, cefr_level} |
| 1.8 | 创建 agents/content_judge.py | 高 | 质量评判 Agent，多维度评分（语法、词汇、连贯性、吸引力），低于阈值则拒绝 |
| 1.9 | 创建 services/article_service.py | 高 | 编排生成管线：调用生成 Agent → 调用评判 Agent → 达标则存储 → 不达标则重试（最多2次） |
| 1.10 | 创建 api/v1/articles.py | 中 | 公开端点：文章列表、文章详情 |
| 1.11 | 创建 api/v1/admin.py | 中 | 管理端点：生成文章、列表（含草稿）、更新状态、删除 |
| 1.12 | 创建 api/v1/router.py | 低 | 聚合路由 |
| 1.13 | 创建文本处理工具 | 中 | 分段、字数统计、阅读时间估算 |
| 1.14 | 添加 Redis 缓存 | 中 | 缓存已发布文章，更新时失效，TTL 1小时 |
| 1.15 | 创建 LLM 客户端封装 | 中 | 封装 openai.AsyncOpenAI，配置 base_url，指数退避重试，超时处理 |
| 1.16 | 编写测试 | 高 | Mock LLM 响应，测试完整管线含重试逻辑，测试 Repository CRUD，测试 API 端点 |
| 1.17 | 前端：文章列表页 | 中 | HomeView：文章卡片展示（标题、难度、字数、主题） |
| 1.18 | 前端：文章详情页 | 中 | ArticleView：段落展示、阅读时间 |
| 1.19 | 前端：管理生成页 | 低 | 简单表单：主题输入、难度选择、生成按钮 |

#### API 端点定义

**公开端点**：

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

**管理端点**：

```
POST /api/v1/admin/articles/generate
  认证：Admin API Key (X-Admin-Key header)
  请求体：
    { "topic": "climate change", "difficulty": "intermediate",
      "target_word_count": 400, "custom_instructions": "..." }
  响应 202: { "task_id": "uuid", "status": "processing" }

GET /api/v1/admin/articles/generation-status/{task_id}
  认证：Admin API Key
  响应 200:
    { "task_id", "status": "completed"|"processing"|"failed",
      "article_id", "quality_score", "generation_attempts", "error" }

GET /api/v1/admin/articles
  认证：Admin API Key
  查询参数：同公开 + include_unpublished=true

PATCH /api/v1/admin/articles/{article_id}
  认证：Admin API Key
  请求体：{ "is_published": true, "difficulty": "advanced" }
  响应 200: 完整文章响应

DELETE /api/v1/admin/articles/{article_id}
  认证：Admin API Key
  响应 204
```

#### 设计模式

1. **Repository 模式**：ArticleRepository 封装所有 SQL 查询，Service 层不直接写查询
2. **Pipeline 模式**（内容生成）：生成 → 评判 → （不达标则带反馈重试）→ 存储，每步独立可扩展
3. **Result 模式**（Agent 输出）：每个 Agent 返回类型化的 Result 对象（Pydantic 模型），而非原始字符串
4. **Cache-Aside 模式**：读文章先查 Redis → 未命中查 DB → 写入 Redis；更新时删除缓存

#### 并发考虑

- **文章生成是慢操作**（5-30秒），不能阻塞 API 响应。返回 `202 Accepted` + task_id，后台任务处理
- **后台任务**：MVP 用 FastAPI BackgroundTasks（同进程），生产环境迁移到 Celery/ARQ
- **LLM 限流**：OpenAI SDK 内置重试+指数退避，额外加 `asyncio.Semaphore(5)` 限制并发 LLM 调用
- **缓存失效**：用 Redis DELETE 而非更新，避免竞态条件

#### 测试策略

| 层 | 测试内容 | 方式 |
|---|---|---|
| Agent 单元 | ContentGenerator 产出有效 JSON | Mock openai.ChatCompletion.create |
| Agent 单元 | ContentJudge 评分逻辑 | Mock LLM，测试低于阈值拒绝、JSON 格式错误 |
| Service | 生成管线编排 | Mock 两个 Agent，测试正常路径、重试路径、最大重试 |
| Repository | CRUD 操作 | 测试数据库，增删改查、过滤、分页 |
| API | 端点 | httpx.AsyncClient，测试列表、详情、生成、状态轮询、404 |

#### 常见陷阱

1. **LLM 返回无效 JSON**：始终 try/except JSON 解析并重试。使用 `response_format: { type: "json_object" }` 或结构化输出
2. **生成超时**：设置 LLM 调用超时（生成 30s、评判 15s）
3. **不要事后分段**：让 LLM 直接生成分段结构（段落数组），事后分段效果差
4. **保存生成元数据**：务必存储 prompt、模型名、token 用量到 generation_metadata
5. **后台任务丢失**：服务器重启时 BackgroundTasks 会丢失，用 Redis 存储 task 状态（设 TTL）

---

### Phase 2：阅读核心

**目标**：用户可以阅读文章并获得四层辅助（词义→短语→句子结构→段落翻译），系统追踪阅读行为。

#### 任务拆分

| # | 任务 | 复杂度 | 详细说明 |
|---|---|---|---|
| 2.1 | 创建 models/reading.py | 中 | ReadingSession、LookupEvent 模型 |
| 2.2 | 创建 Alembic 迁移 | 低 | |
| 2.3 | 创建 schemas/reading.py | 中 | Session Create/Response/Update, LookupEvent Create/Response, AssistanceRequest/Response |
| 2.4 | 创建 repositories/reading_repo.py | 中 | create_session(), get_session(), update_session(), add_lookup_event() |
| 2.5 | 创建 agents/reading_assistant.py | 高 | 统一 Agent，根据 assistance_type 切换提示词策略，处理四层辅助 |
| 2.6 | 创建 agents/grammar_analyzer.py | 高 | 分析句子结构，返回 {sentence, components: [{text, role}]} |
| 2.7 | 创建 services/reading_service.py | 高 | 会话管理（开始、更新进度、结束），计算阅读速度，聚合查词事件，调用 Assistant Agent |
| 2.8 | 创建 api/v1/reading.py | 中 | 会话管理和辅助端点 |
| 2.9 | 添加辅助结果缓存 | 中 | 词义/短语缓存，key: `assist:{hash(text)}:{type}`，TTL 24小时 |
| 2.10 | 补充 text_processing.py | 中 | 提取选中文本、获取上下文段落 |
| 2.11 | 编写后端测试 | 高 | 会话生命周期、辅助缓存、查词记录 |
| 2.12 | 编写 Agent 测试 | 中 | Mock LLM，测试每种辅助类型 |
| 2.13 | 前端：ArticleReader.vue | 高 | 主阅读组件，段落展示、文本选择、进度条 |
| 2.14 | 前端：辅助组件 | 高 | WordTooltip、PhrasePanel、SentenceBreakdown、ParagraphTranslation |
| 2.15 | 前端：useReadingSession | 中 | 管理会话状态：开始、每30s更新进度、记录查词、离开时结束 |
| 2.16 | 前端：useTextSelection | 中 | 检测文本选择、提取选中文本、判断选择类型（词/短语/句子） |
| 2.17 | 前端：useAssistance | 中 | 调用辅助 API、管理加载状态、客户端缓存结果 |
| 2.18 | 前端：组装阅读页 | 中 | ReadingView.vue 组合所有组件 |
| 2.19 | 编写 E2E 测试 | 高 | Playwright：打开文章→阅读→选词→看释义→选短语→看解释→完成 |

#### API 端点定义

```
POST /api/v1/reading/sessions
  认证：无（Phase 3 加认证）
  请求体：{ "article_id": "uuid" }
  响应 201: { "session_id", "article_id", "started_at", "status": "active" }

PATCH /api/v1/reading/sessions/{session_id}
  请求体：{ "segments_read": 5, "completion_percentage": 0.75 }
  响应 200: { "session_id", "status", "completion_percentage", "duration_seconds" }

POST /api/v1/reading/sessions/{session_id}/complete
  请求体：{ "total_duration_seconds": 240 }
  响应 200: { "session_id", "status": "completed", "words_per_minute": 112, "words_looked_up": 8 }

POST /api/v1/reading/assist
  请求体：
    { "text": "ephemeral", "context": "The nature of...",
      "assistance_type": "word"|"phrase"|"sentence"|"paragraph",
      "article_id": "uuid", "native_language": "zh" }
  响应 200:
    // word 类型：
    { "word", "pronunciation", "definition_en", "definition_native",
      "part_of_speech", "example_sentence", "difficulty", "cefr_level" }
    // phrase 类型：
    { "phrase", "meaning_en", "meaning_native", "usage_notes", "examples"[] }
    // sentence 类型：
    { "original", "structure_breakdown": [{ "clause", "role" }],
      "simplified", "translation" }
    // paragraph 类型：
    { "translation", "key_points": string[] }

POST /api/v1/reading/sessions/{session_id}/lookups
  请求体：{ "segment_index": 3, "selected_text": "ephemeral",
            "lookup_type": "word", "result_snapshot": {...} }
  响应 201: { "lookup_id", "created_at" }

GET /api/v1/reading/sessions/{session_id}/lookups
  响应 200: { "lookups": [...] }
```

#### 设计模式

1. **策略模式**（辅助类型）：ReadingAssistantAgent 内部根据 assistance_type 选择不同提示词模板和输出解析器
2. **观察者模式**（阅读事件）：查词事件作为副效应异步记录，不影响辅助响应速度
3. **Composable 模式**（前端）：useReadingSession、useTextSelection、useAssistance 封装有状态逻辑

#### 并发考虑

- **辅助请求频繁**：用户点击多个词。Redis 缓存是第一道防线，常见词几乎总是缓存命中
- **客户端防抖**：前端 300ms 防抖，用户快速切换选择时取消前一个请求
- **进度更新限流**：Redis 记录上次更新时间，15秒内跳过重复更新
- **句子/段落分析限并发**：Semaphore 限制同时 3 个高成本 LLM 调用

#### 常见陷阱

1. **跨段落文本选择**：用户可能选中跨两段的内容，前端需处理这种情况
2. **阅读时间不准确**：用活跃阅读时间（页面可见+近期滚动），而非起止时间差
3. **辅助面板遮挡文本**：窄屏用底部抽屉，宽屏用侧边栏，必须从开始就设计响应式
4. **LLM 编造释义**：系统提示词中要求只用标准词典定义，不确定时说"未找到释义"
5. **用户关闭页面丢进度**：用 beforeunload 发送最终进度更新，同时每 30s 自动保存

---

### Phase 3：用户系统与语料库

**目标**：用户注册/登录、问卷定级、个人语料库（保存/复习/导出）、基础推荐。

#### 任务拆分

| # | 任务 | 复杂度 | 详细说明 |
|---|---|---|---|
| 3.1 | 创建 models/user.py | 中 | User, UserPreference 模型 |
| 3.2 | 创建迁移 | 低 | |
| 3.3 | 创建 schemas/auth.py | 中 | RegisterRequest, LoginRequest, TokenResponse, UserResponse, OnboardingRequest |
| 3.4 | 创建 utils/security.py | 中 | hash_password(), verify_password(), create_access_token(), decode_access_token()。用 passlib[bcrypt] + python-jose |
| 3.5 | 创建 repositories/user_repo.py | 中 | get_by_email(), create_user(), update_user() |
| 3.6 | 创建 services/auth_service.py | 高 | register()、login()、get_current_user()。Token 有效期 7 天 |
| 3.7 | 创建 api/v1/auth.py | 中 | POST /auth/register, /auth/login, GET /auth/me, PATCH /auth/me, POST /auth/onboarding |
| 3.8 | 更新 dependencies.py | 中 | 添加 get_current_user() 依赖：提取 Bearer token、验证 JWT、返回用户对象 |
| 3.9 | 创建 models/corpus.py | 中 | CorpusEntry, ReviewLog 模型 |
| 3.10 | 创建迁移 | 低 | |
| 3.11 | 创建 schemas/corpus.py | 中 | CorpusEntryCreate/Response/Update, ReviewSubmitRequest/Response, ExportRequest |
| 3.12 | 创建 repositories/corpus_repo.py | 中 | CRUD + find_duplicate(), get_due_reviews() |
| 3.13 | 创建 services/corpus_service.py | 高 | 保存（查重+初始SRS状态）、查询、更新、删除、导出 |
| 3.14 | 集成 FSRS 库 | 高 | 安装 fsrs 包，创建 srs_service.py 封装算法 |
| 3.15 | 创建 api/v1/corpus.py | 中 | 语料库 CRUD + 复习端点 |
| 3.16 | 创建 recommendation_service.py | 高 | MVP 用简单启发式：匹配难度、排除已读文章、优先有未知词汇的主题 |
| 3.17 | 更新 articles.py | 低 | 添加 GET /articles/recommended（需认证） |
| 3.18 | 创建问卷引导流程 | 中 | 多步表单向导 |
| 3.19 | 编写认证测试 | 高 | 注册、登录、token 验证、过期 token、重复邮箱 |
| 3.20 | 编写语料库测试 | 高 | CRUD、去重、FSRS 复习周期、导出 |
| 3.21 | 前端：认证页面 | 中 | 登录、注册页，token 存 localStorage，Axios 拦截器加 Bearer |
| 3.22 | 前端：问卷引导 | 中 | 多步表单向导组件 |
| 3.23 | 前端：语料库页面 | 高 | CorpusView：按类型过滤、搜索、分页，从阅读页一键保存 |
| 3.24 | 前端：复习页 | 高 | 闪卡式复习：显示词条→用户评分(Again/Hard/Good/Easy)→显示答案 |
| 3.25 | 前端：导出功能 | 低 | 下载 CSV/JSON |
| 3.26 | 更新阅读会话关联用户 | 中 | 阅读端点加认证，存储 user_id，查词自动保存到语料库（用户可选） |

#### API 端点定义

```
POST /api/v1/auth/register
  请求体：{ "email", "password", "display_name" }
  响应 201: { "user": {...}, "access_token", "token_type": "bearer" }
  响应 409: {"detail": "Email already registered"}

POST /api/v1/auth/login
  请求体：{ "email", "password" }
  响应 200: { "access_token", "token_type", "user": {...} }
  响应 401: {"detail": "Invalid credentials"}

GET /api/v1/auth/me
  认证：Bearer token
  响应 200: { "id", "email", "display_name", "level", "corpus_stats": {...}, ... }

POST /api/v1/auth/onboarding
  认证：Bearer token
  请求体：{ "current_level", "learning_goal", "target_exam", "target_score",
            "interests": ["technology", "science"], "daily_goal_minutes" }
  响应 200: { "user": {...}, "recommended_articles": [...] }

GET /api/v1/corpus
  认证：Bearer token
  查询参数：entry_type, search, sort, order, page, page_size
  响应 200: { "items": [{ "id", "entry_type", "content", "context", "translation",
              "review_count", "next_review", ... }], "total", "page" }

POST /api/v1/corpus
  认证：Bearer token
  请求体：{ "entry_type", "content", "context", "source_article_id",
            "translation", "definition", "cefr_level" }
  响应 201: 完整条目
  响应 409: {"detail": "Entry already exists in corpus"}

DELETE /api/v1/corpus/{entry_id}
  认证：Bearer token（必须拥有该条目）
  响应 204

GET /api/v1/corpus/reviews/due
  认证：Bearer token
  查询参数：limit(default 20), entry_type
  响应 200: { "items": [...], "total_due", "returned" }

POST /api/v1/corpus/{entry_id}/review
  认证：Bearer token
  请求体：{ "rating": 3 }  // 1=Again, 2=Hard, 3=Good, 4=Easy
  响应 200: { "next_review", "srs_interval_days", "review_count" }

GET /api/v1/corpus/export
  认证：Bearer token
  查询参数：format(csv|json), entry_type
  响应 200: 文件下载

GET /api/v1/articles/recommended
  认证：Bearer token
  查询参数：limit(default 5)
  响应 200: { "articles": [{..., "match_reason": "..."}] }
```

#### 设计模式

1. **依赖注入（认证）**：get_current_user 作为 FastAPI 依赖注入到需要认证的端点
2. **值对象（SRS 状态）**：FSRS 卡片状态用 Pydantic 模型（SRSState）序列化到 JSONB
3. **工厂方法（语料条目）**：不同 entry_type 有不同创建逻辑（词自动获取释义，短语自动获取搭配）

#### 并发考虑

- **JWT 无状态**：不需要 DB 查询验证 token，快速。代价是需要 Redis 黑名单实现 token 撤销
- **FSRS 状态更新原子性**：复习时 FSRS 状态更新和 review_log 创建在同一事务中
- **语料去重**：数据库唯一约束 `(user_id, entry_type, content)` 防止并发保存重复
- **复习批处理**：前端批量发送复习结果（每 10 个一批），避免 50 个卡片 50 次 API 调用

#### 常见陷阱

1. **密码存储**：始终用 bcrypt（work factor 12），绝不用 MD5/SHA256
2. **JWT 密钥管理**：必须在环境变量中，开发用 .env，生产用密钥管理器
3. **FSRS 集成**：仔细读 fsrs 库文档，核心概念是 Card、Rating、ReviewLog、Scheduler
4. **语料库无限增长**：500 条时软提示"先复习再添加"，不硬性阻止
5. **忘记关联来源文章**：context_source_id 对"在上下文中复习"功能至关重要

---

### Phase 4：理解反馈与 MVP 完善

**目标**：生成理解题、评估答案、学习仪表盘、生产部署。MVP 完成。

#### 任务拆分

| # | 任务 | 复杂度 | 详细说明 |
|---|---|---|---|
| 4.1 | 创建 models/feedback.py | 中 | QuizQuestion, QuizResponse 模型 |
| 4.2 | 创建迁移 | 低 | |
| 4.3 | 创建 schemas/feedback.py | 中 | QuizQuestionResponse, QuizSubmitRequest/Response |
| 4.4 | 创建 agents/question_generator.py | 高 | 生成 1-3 道理解题（选择题/判断题/简答题），返回结构化 JSON |
| 4.5 | 创建 services/feedback_service.py | 高 | generate_quiz()、submit_answer()（选择题精确匹配，简答题 LLM 评估）|
| 4.6 | 创建 api/v1/feedback.py | 中 | 测验端点 |
| 4.7 | 缓存生成的测验 | 中 | 按文章 ID 缓存，首次请求后生成 |
| 4.8 | 创建 dashboard_service.py | 中 | 聚合：已读文章、总时长、语料量、复习正确率、连续天数 |
| 4.9 | 创建 api/v1/dashboard.py | 低 | 仪表盘端点 |
| 4.10 | 编写测验测试 | 高 | 题目生成、答案评估、分数计算 |
| 4.11 | 前端：测验组件 | 高 | 选择题单选按钮、简答题输入、提交显示结果 |
| 4.12 | 前端：仪表盘页面 | 中 | 统计卡片 + 简单柱状图（每日活动） |
| 4.13 | 前端：响应式和完善 | 中 | 移动端适配、加载状态、错误状态、空状态 |
| 4.14 | 全链路集成测试 | 高 | 完整用户旅程：注册→问卷→推荐→阅读→辅助→保存→测验→仪表盘→复习 |
| 4.15 | 生产部署配置 | 高 | Docker Compose 生产配置、Nginx + SSL、部署脚本、数据库备份 |
| 4.16 | 错误处理审计 | 中 | 确保所有 API 返回正确错误，前端友好错误信息，LLM 失败优雅降级 |
| 4.17 | 性能测试 | 中 | 阅读端点负载测试、数据库查询优化、缓存命中率 |
| 4.18 | 文档 | 中 | API 文档（FastAPI 自动生成）、README 部署指南 |

#### API 端点定义

```
GET /api/v1/articles/{article_id}/quiz
  认证：Bearer token
  响应 200:
    { "article_id", "questions": [
        { "id", "question_text", "question_type", "options", "difficulty" }
      ] }

POST /api/v1/feedback/quiz/{question_id}/answer
  认证：Bearer token
  请求体：{ "session_id", "answer", "time_taken_seconds" }
  响应 200:
    { "question_id", "is_correct", "user_answer", "correct_answer",
      "explanation", "score"(简答题 0-1) }

GET /api/v1/reading/sessions/{session_id}/results
  认证：Bearer token
  响应 200:
    { "session_id", "article_title",
      "reading_stats": { "duration_seconds", "words_per_minute", "words_looked_up" },
      "quiz_stats": { "total_questions", "correct_answers", "score_percentage" } }

GET /api/v1/dashboard
  认证：Bearer token
  查询参数：period(week|month|all)
  响应 200:
    { "reading_stats": { "articles_read", "total_reading_time_minutes",
        "average_reading_speed_wpm", "reading_streak_days" },
      "corpus_stats": { "total_entries", "reviews_completed", "review_accuracy", "due_for_review" },
      "quiz_stats": { "quizzes_taken", "average_score" },
      "daily_activity": [{ "date", "articles_read", "reading_minutes", "reviews_done" }],
      "level_progress": { "current_level", "estimated_cefr", "progress_to_next" } }
```

#### 设计模式

1. **模板方法（出题）**：QuestionGeneratorAgent 固定流程（读文章→出题→验证），不同题型用策略实现
2. **Facade（仪表盘）**：DashboardService 聚合多个服务数据为单一响应，前端一次调用
3. **熔断器（LLM 调用）**：连续 5 次失败后暂停 60 秒，优雅降级（显示"暂时不可用"）

#### 生产部署架构

```
Nginx（SSL终结 + 静态文件 + 反向代理）
  └── Docker Compose
      ├── FastAPI (uvicorn, 2 workers)
      ├── PostgreSQL 16 (持久卷)
      └── Redis 7 (持久化)
```

#### 常见陷阱

1. **测验难度不匹配**：出题 Agent 必须知道文章难度和用户水平，都写入 prompt
2. **简答题评估不稳定**：用 0-1 评分制而非二元对错，展示评分和参考答案
3. **仪表盘查询慢**：预计算每日统计到 user_daily_stats 表，夜间后台任务更新
4. **空数据状态**：新用户看到空仪表盘，设计有意义的空状态提示
5. **部署忘迁移**：部署脚本必须：拉代码 → alembic upgrade head → 重启应用

---

## 五、跨阶段通用规范

### 错误处理模式

统一错误响应格式：
```json
{
  "detail": "人类可读消息",
  "error_code": "ARTICLE_NOT_FOUND",
  "errors": [{ "field": "email", "message": "格式无效" }]
}
```

实现方式：
- 自定义异常层级：AppException → NotFoundException / ValidationException / UnauthorizedException / ExternalServiceException
- 在 FastAPI exception_handlers 中统一注册
- Service 层抛异常，API 层不需要 try/except

LLM 特定错误：
- 超时 → 503 "AI 助手暂时不可用"
- 返回无效 JSON → 重试 2 次，仍失败则返回降级响应
- 限流 429 → 指数退避，3 次后仍失败则 503

### 环境与依赖管理

**后端**：
- pyproject.toml 管理项目元数据和开发依赖
- requirements.txt（pip freeze 生成）管理生产依赖，版本锁定
- venv 虚拟环境（不用 Conda）
- Python 3.11+

**前端**：
- package.json 精确版本
- Node 20 LTS（.nvmrc 指定）
- pnpm 安装

### 关键库版本

| 库 | 用途 | 版本 |
|---|---|---|
| FastAPI | Web 框架 | 0.115+ |
| SQLAlchemy | ORM | 2.0+ |
| asyncpg | PG 异步驱动 | 0.30+ |
| Alembic | 迁移 | 1.13+ |
| pydantic | 数据校验 | 2.0+ |
| redis | 缓存/队列 | 5.0+ |
| openai | LLM 客户端 | 1.30+ |
| python-jose | JWT | 3.3+ |
| passlib | 密码哈希 | 1.7+ |
| httpx | 测试用 HTTP 客户端 | 0.27+ |
| ruff | 后端 lint + format | 0.5+ |
| Vue 3 | 前端框架 | 3.4+ |
| Vite | 构建工具 | 5.0+ |
| Pinia | 状态管理 | 2.1+ |
| TailwindCSS | 样式 | 4.0+ |
| fsrs | 间隔重复 | 4.0+ |

### 测试策略总览

| 层 | 工具 | 范围 |
|---|---|---|
| 单元测试 | pytest + pytest-asyncio | Services, Repositories, Agents, Utils |
| API 测试 | pytest + httpx | 所有端点（用测试数据库）|
| 前端单元 | Vitest | 组件、composables、stores |
| 前端 E2E | Playwright | 关键用户旅程 |
| 集成测试 | pytest | 完整管线：Agent → Service → Repo → DB |

测试数据库：独立的 `ai_reading_test`，conftest.py 创建，每个测试在事务中运行并回滚。

---

## 六、验证方案

### 每个阶段结束时验证

- **Phase 0**：`docker-compose up` → 访问 `localhost:8000/health` → 看到数据库和 Redis 都 connected
- **Phase 1**：`POST /admin/articles/generate` → 轮询状态 → 文章生成成功 → `GET /articles` 能看到
- **Phase 2**：打开文章 → 点击单词看到释义 → 展开段落翻译 → 完成阅读看到统计
- **Phase 3**：注册 → 登录 → 完成问卷 → 保存词条到语料库 → 复习卡片
- **Phase 4**：阅读文章 → 做题 → 看到分数 → 打开仪表盘看到统计数据

### MVP 完成验证

完整用户旅程：
1. 注册新账号 → 登录
2. 完成定级问卷
3. 看到个性化推荐文章
4. 阅读文章，使用四层辅助
5. 保存词条到语料库
6. 完成理解题，查看结果
7. 打开仪表盘，看到学习数据
8. 复习语料库中的卡片
9. 导出语料库为 JSON/CSV

### 关键文件清单

这些文件是项目骨架，实现时最先创建：

- `backend/app/config.py` — 全局配置，所有文件依赖
- `backend/app/database.py` — 数据库连接，所有数据访问依赖
- `backend/app/agents/base.py` — Agent 基类，所有 LLM Agent 继承
- `backend/app/repositories/base.py` — 泛型 Repository，所有数据访问继承
- `docker-compose.yml` — 开发环境，配置错误则一切无法运行
