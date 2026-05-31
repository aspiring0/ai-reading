# 总体架构

> 从 `2026-05-31-ai-reading-technical-blueprint.md` 提取的架构总览
> 跨阶段通用，开发时作为参考

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

### 关键设计决策

- **为什么分 Repository 层**：将数据访问与业务逻辑解耦，Service 层不写 SQL，测试时 mock Repository 即可
- **为什么 schemas/ 与 models/ 分开**：SQLAlchemy 模型定义数据库形状，Pydantic 模型定义 API 形状，二者经常不同（如响应排除密码哈希）
- **为什么 agents/ 与 services/ 分开**：Agent 是 LLM 特定逻辑（提示词工程、输出解析），Service 编排 Agent 和 Repository，分开可独立测试

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
| PyJWT | JWT | 2.8+ |
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
