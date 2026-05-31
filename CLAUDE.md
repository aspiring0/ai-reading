# AI 英语阅读产品 - Claude 项目约束

## 项目概述

AI 英语阅读学习应用，以多智能体 AIGC 为核心。用户通过阅读 AI 生成/推荐的英语文章，获得分层辅助、个人语料库、间隔复习等学习功能。

产品方案原文：`D:\A_my\笔记\产品思路\英文文章阅读器.md`
技术蓝图：`docs/2026-05-31-ai-reading-technical-blueprint.md`

## 技术栈（不可更改）

- **后端**：Python 3.11+ / FastAPI / SQLAlchemy 2.0 (async) / asyncpg / Alembic
- **数据库**：PostgreSQL 16 / Redis 7
- **前端**：Vue 3 (Composition API + `<script setup>`) / TypeScript / Pinia / TailwindCSS / Vite
- **LLM**：OpenAI SDK 直连（通过 `base_url` 配置支持任何 OpenAI 兼容 API，如 DeepSeek、Ollama、Azure OpenAI 等。不用 LangChain/AutoGen 等框架）
- **SRS**：fsrs Python 库
- **容器**：Docker + Docker Compose
- **代码规范**：后端 ruff / 前端 eslint + prettier
- **测试**：后端 pytest + pytest-asyncio + httpx / 前端 Vitest + Playwright
- **包管理**：uv（`uv venv` 创建虚拟环境，`uv pip install` 安装依赖）

### 依赖管理规范

- `pyproject.toml` — 声明依赖版本范围（开发依赖在 `[project.optional-dependencies]` dev 下）
- `requirements.txt` — 由 `uv pip freeze > requirements.txt` 生成，锁定精确版本，用于生产部署
- 虚拟环境在 `backend/.venv/`，不提交到 git
- 新增依赖：先加到 `pyproject.toml`，再 `uv pip install -e ".[dev]"`，再 `uv pip freeze > requirements.txt`

## 架构原则

### 分层架构（严格遵守）

```
API 端点层 (api/) → Service 层 (services/) → Repository 层 (repositories/)
                                  ↕
                           Agent 层 (agents/)
```

- **API 层**只做参数校验和调用 Service，不包含业务逻辑
- **Service 层**编排业务逻辑，调用 Repository 和 Agent，不直接写 SQL
- **Repository 层**封装所有数据库操作，返回 ORM 模型对象
- **Agent 层**封装 LLM 交互（提示词工程、输出解析），独立于业务逻辑
- **schemas/**（Pydantic）和 **models/**（SQLAlchemy）必须分开

### 禁止事项

- 不使用 LangChain、AutoGen、CrewAI 等 LLM 框架
- 不在 Service 层写 SQL 查询（必须通过 Repository）
- 不在 API 层写业务逻辑
- 不硬编码密钥、密码、token
- 不使用同步数据库驱动（必须 asyncpg）
- 不跳过 Alembic 迁移直接改数据库
- 不提交 `.env` 文件到 git
- 不使用 MD5/SHA256 存密码（必须 bcrypt）

## 代码规范

### Python

- 使用 type hints，所有函数签名必须标注参数和返回类型
- 使用 `async/await`，所有数据库操作和 LLM 调用必须是异步的
- Pydantic v2 风格（`model_config` 而非 `class Config`）
- SQLAlchemy 2.0 风格（`Mapped`、`mapped_column`）
- 使用 Python 3.11+ 语法（`str | None` 而非 `Optional[str]`）

### TypeScript/Vue

- Vue 3 Composition API + `<script setup lang="ts">`
- 使用 composables 封装有状态逻辑（`useXxx.ts`）
- Pinia store 用 setup 风格（`defineStore('name', () => {...})`）
- API 调用封装在 `src/api/` 目录，不直接在组件中调用 Axios

### 文件命名

- Python：snake_case（`article_service.py`）
- Vue 组件：PascalCase（`ArticleReader.vue`）
- composables：camelCase 以 use 开头（`useReadingSession.ts`）
- 测试文件：`test_<module>.py`

## Git 工作流

- **分支策略**：GitHub Flow（main / develop / feature/Px-xxx）
- **提交规范**：Conventional Commits（`feat(scope): desc` / `fix(scope): desc`）
- **scope 示例**：api, db, agents, ui, ci, config
- 每个功能分支对应计划书中的一个任务
- 合并前必须 lint + test 通过

## 数据库

- 所有表变更必须通过 Alembic 迁移
- 连接串格式：`postgresql+asyncpg://user:pass@host:5432/dbname`
- 使用 UUID 作为主键
- 时间字段统一用 TIMESTAMPTZ
- JSONB 用于灵活数据（SRS 状态、生成元数据等）
- 每个表必须有 `created_at` 字段

## 错误处理

- 统一错误响应格式：`{ "detail": "消息", "error_code": "CODE", "errors": [...] }`
- 自定义异常层级：AppException → NotFound / Validation / Unauthorized / ExternalService
- Service 层抛异常，API 层不需要 try/except（FastAPI exception_handler 统一处理）
- LLM 调用失败必须优雅降级（重试 → 降级响应 → 503）

## 测试要求

- 每个新增功能必须有对应的测试
- 测试文件结构与源码对应（`test_api/`, `test_services/`, `test_agents/`）
- 测试数据库独立（`ai_reading_test`），每个测试在事务中回滚
- Agent 测试通过 mock LLM 响应，不调用真实 API
- API 测试使用 httpx.AsyncClient + ASGITransport

## LLM Agent 规范

- 所有 Agent 继承 `agents/base.py` 的 BaseAgent
- Agent 返回类型化的 Pydantic Result 对象，不返回原始字符串
- LLM 返回 JSON 必须有 try/except + 重试机制
- 系统 prompt 与用户 prompt 分离管理
- 保存每次调用的 prompt 和元数据用于调试

## 安全

- 密码：bcrypt，work factor 12
- JWT：使用 PyJWT（不用 python-jose，已不维护），密钥从环境变量读取，token 有效期 7 天
- CORS：开发环境允许 localhost:5173，生产环境限制为实际域名
- 输入校验：所有 API 输入通过 Pydantic schema 校验
- SQL 注入：使用 SQLAlchemy ORM，不拼接 SQL

## 日志规范

- 使用 structlog（结构化日志，JSON 输出，方便生产环境日志收集）
- 级别策略：
  - DEBUG：开发环境详细调试（SQL 查询、LLM 请求/响应）
  - INFO：业务事件（用户注册、文章生成、阅读完成）
  - WARNING：降级事件（LLM 重试、缓存未命中回源）
  - ERROR：需要关注的错误（LLM 连续失败、数据库连接断开）
- 禁止在日志中输出：密码、token、完整 LLM prompt（只记录前 100 字符 + token 数）
- Agent 每次调用记录：model, prompt_hash, input_tokens, output_tokens, duration_ms, success

## 前端路由守卫

- 未登录访问需认证页面（/corpus, /dashboard, /settings）→ 跳转 /login?redirect=原路径
- 已登录访问 /login, /register → 跳转首页
- onboarding_complete=false 的用户访问任何页面 → 跳转 /onboarding
- 路由守卫统一在 router/index.ts 的 beforeEach 中处理，不在组件中单独判断

## 前端错误处理

- Axios 响应拦截器统一处理：
  - 401 → 清除 token，跳转 /login
  - 403 → toast "无权限"
  - 404 → toast "资源不存在"
  - 422 → 提取 errors 数组，展示字段级错误
  - 500/503 → toast "服务暂时不可用，请稍后重试"
- 组件内不处理上述通用错误，只处理业务特有错误（如"词条已存在"）
- LLM 相关功能加载中必须显示骨架屏或 loading 状态，不能空白

## API 版本化

- 当前版本 v1，所有端点在 /api/v1/ 下
- 引入 v2 的条件：破坏性变更（删除字段、改字段类型、改语义）
- 新增字段、新增端点不算破坏性变更，在 v1 内演进
- v2 引入后 v1 至少保留 3 个月
- 版本路由文件：api/v1/router.py, api/v2/router.py

## 环境变量

- 命名：大写 + 下划线，分组前缀（DB_, REDIS_, LLM_, AUTH_, CORS_）
- 必需变量在 config.py 中无默认值（启动即报错）
- 可选变量提供合理默认值
- .env.example 必须列出所有变量及说明
- 敏感变量（SECRET_KEY, API_KEY）绝不提交到 git

## 文档管理

- 文档根目录：docs/
- 结构规范见 docs/README.md
- 每个 Phase 的执行计划在 docs/phases/ 下独立文件
- 技术决策用 ADR 格式记录在 docs/decisions/
- 原始蓝图归档不动，拆分后的 Phase 文件是执行版

## 开发工作流（严格遵守）

每个 Checkpoint 必须按以下顺序执行，未完成验证不得进入下一步：

### 1. 执行任务
- 从当前 Phase 文件中读取当前 Checkpoint 的任务
- 在 feature 分支上开发（`feature/P0a-xxx`）

### 2. 自动测试
- 运行 `pytest` 确认新写的测试通过
- 运行 `ruff check` 确认代码规范

### 3. 实际运行验证（不能跳过）
- 启动服务（`docker-compose up` 或 `uvicorn`）
- 手动验证当前 Checkpoint 的功能确实可用
- 验证命令示例：
  - `curl http://localhost:8000/health` — 确认服务启动
  - `curl http://localhost:8000/api/v1/articles` — 确认 API 返回数据
  - 浏览器打开前端页面 — 确认页面正常渲染
- 如果实际运行出错，必须在此步骤修复，不能留到后面

### 4. 提交检查点
- 确认自动测试 + 实际运行都通过后，才能 git commit
- commit message 格式：`feat(scope): 描述` 或 `chore(scope): 描述`
- 合并到 develop 分支

### 5. 更新进度
- 在 Phase 文件中将已完成任务的状态从 ⬜ 改为 ✅

### 如果出了问题
- 在 feature 分支上出错 → `git checkout .` 丢弃改动重做
- 已合并到 develop 但发现问题 → `git revert <commit>` 回到上一个检查点
- 不知道哪步出错 → 回到上一个 ✅ 状态，逐步重做

## 数据模型注意项

- Phase 2 创建 reading_sessions 时，user_id 列设为 nullable UUID
  - Phase 2 无认证时 user_id=NULL
  - Phase 3a 加认证后填充 user_id
  - 避免 Phase 3 大改迁移
