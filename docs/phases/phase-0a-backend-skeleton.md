# Phase 0a: 后端骨架

## 目标

搭建可运行的后端项目骨架，包含数据库、缓存、CI/CD、开发环境配置，以及一个健康检查端点。完成后可通过 `docker-compose up` 启动全部后端基础设施并验证连通性。

## 前置条件

- 无（这是项目的第一个阶段）

## 检查点

### Checkpoint 0a-1: 项目初始化
**任务**: 0.1, 0.2, 0.3
**Git 分支**: `feature/P0a-1-init-project`
**Git commit**: `chore: init project structure and dependencies`

验证步骤：
1. `ls backend/app/` — 确认目录结构存在
2. `cd backend && pip install -e .` — 确认依赖能安装
3. `ruff check backend/` — 确认无 lint 错误

### Checkpoint 0a-2: 开发环境
**任务**: 0.4, 0.10, 0.11
**Git 分支**: `feature/P0a-2-dev-env`
**Git commit**: `chore(ci): add docker-compose, Makefile, and env config`

验证步骤：
1. `docker-compose up -d postgres redis` — 容器启动无报错
2. `docker-compose ps` — postgres 和 redis 状态都是 healthy
3. `make migrate` — 能执行（即使没有迁移文件也不报错）

### Checkpoint 0a-3: 应用核心
**任务**: 0.5, 0.6, 0.7
**Git 分支**: `feature/P0a-3-app-core`
**Git commit**: `feat(api): add FastAPI app with config and health endpoint`

验证步骤：
1. `cd backend && uvicorn app.main:app --reload` — 应用启动无报错
2. 浏览器打开 `http://localhost:8000/docs` — 能看到 Swagger 文档
3. `curl http://localhost:8000/health` — 返回 `{"status":"ok",...}`
4. 停掉 postgres → `curl /health` → 看到 `"database":"disconnected"`

### Checkpoint 0a-4: 数据库迁移 + 基础模块
**任务**: 0.8, 0.9, 0.12, 0.13
**Git 分支**: `feature/P0a-4-db-and-modules`
**Git commit**: `feat(db): add Alembic migration and base modules`

验证步骤：
1. `alembic upgrade head` — 迁移执行成功
2. `alembic current` — 显示当前迁移版本
3. 重启 uvicorn → `curl /health` — 仍然正常

### Checkpoint 0a-5: CI + 测试 + Docker
**任务**: 0.18, 0.19b, 0.20, 0.21b
**Git 分支**: `feature/P0a-5-ci-and-tests`
**Git commit**: `chore(ci): add GitHub Actions, health test, and Dockerfile`

验证步骤：
1. `cd backend && pytest` — 测试通过，显示 1 passed
2. `ruff check backend/` — 无 lint 错误
3. `docker build -t ai-reading-backend ./backend` — Dockerfile 构建成功
4. 推送 PR 到 develop → GitHub Actions CI 全绿

## 任务清单

| # | 任务 | 复杂度 | 状态 |
|---|---|---|---|
| 0.1 | 初始化 git 仓库：`git init`，创建 `.gitignore`（Python + Node + IDE 模板） | 低 | ✅ |
| 0.2 | 创建目录结构：按蓝图第二章的 backend 目录创建空目录和 `__init__.py` | 低 | ✅ |
| 0.3 | 创建 pyproject.toml：核心依赖 fastapi, uvicorn, sqlalchemy[asyncio], asyncpg, alembic, pydantic-settings, redis, openai, PyJWT, passlib[bcrypt], httpx, ruff | 低 | ✅ |
| 0.4 | 创建 docker-compose.yml：服务 postgres (5432)、redis (6379)，带 volume 持久化和健康检查 | 中 | ⬜ |
| 0.5 | 创建 config.py：pydantic-settings BaseSettings，字段 DATABASE_URL, REDIS_URL, SECRET_KEY, OPENAI_API_KEY, OPENAI_BASE_URL, CORS_ORIGINS, ENV | 中 | ⬜ |
| 0.6 | 创建 database.py：异步引擎、async sessionmaker、`get_db()` 依赖。连接串必须用 `postgresql+asyncpg://` | 中 | ⬜ |
| 0.7 | 创建 main.py：FastAPI 实例，注册 CORS 中间件，lifespan 处理 Redis 连接/断开，挂载 v1 路由，添加 `/health` 端点 | 中 | ⬜ |
| 0.8 | 初始化 Alembic：`alembic init alembic`，配置 `env.py` 使用异步引擎并导入模型 | 中 | ⬜ |
| 0.9 | 创建初始迁移：`alembic revision --autogenerate -m "initial"` | 低 | ⬜ |
| 0.10 | 创建 Makefile：目标 `dev`(docker-compose up), `migrate`, `test`, `lint`, `format` | 低 | ⬜ |
| 0.11 | 创建 .env.example：文档化所有必需的环境变量 | 低 | ⬜ |
| 0.12 | 创建 exceptions.py：异常层级 AppException -> NotFoundException / ValidationException / ExternalServiceException | 低 | ⬜ |
| 0.13 | 创建 dependencies.py：共享依赖 get_db(), get_redis(), get_current_user()（暂为桩） | 低 | ⬜ |
| 0.18 | 配置 GitHub Actions CI：PR 触发后端 lint (ruff) + test (pytest) | 中 | ⬜ |
| 0.19b | 配置后端代码规范工具：ruff（在 pyproject.toml 中配置） | 低 | ⬜ |
| 0.20 | 编写第一个测试：测试 `GET /health` 返回 200，用 httpx.AsyncClient + ASGITransport | 低 | ⬜ |
| 0.21b | 创建后端 Dockerfile：多阶段构建 | 中 | ⬜ |

## API 端点

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

## 数据模型变更

本阶段无业务数据模型。仅创建基础设施文件（config、database、exceptions、dependencies）。

## 设计模式

- **依赖注入**：`get_db()`, `get_redis()` 作为 FastAPI 依赖注入，便于测试时覆盖
- **异常层级**：所有自定义异常继承 `AppException`，在 FastAPI exception_handlers 中统一注册，Service 层抛异常，API 层不需要 try/except
- **统一错误响应格式**：
  ```json
  {
    "detail": "人类可读消息",
    "error_code": "ARTICLE_NOT_FOUND",
    "errors": [{ "field": "email", "message": "格式无效" }]
  }
  ```

## 测试要求

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

## Git 工作流

**分支策略**：GitHub Flow
- `main` -- 生产代码，受保护，合并需要 CI 通过
- `develop` -- 集成分支，所有功能分支先合并到这里
- `feature/P0-xxx-description` -- 功能分支，如 `feature/P0-setup-database`

**提交规范**：Conventional Commits
- `feat(scope): 描述` -- 新功能
- `fix(scope): 描述` -- 修复
- `chore(scope): 描述` -- 构建、CI、工具
- `refactor(scope): 描述` -- 重构
- `test(scope): 描述` -- 测试
- scope 示例：api, db, agents, ui, ci

**PR 流程**：
1. 从 develop 创建功能分支
2. 提交代码
3. 推送并创建 PR 到 develop
4. CI 必须通过（lint + test）
5. 自查 diff 后合并

## 陷阱

1. **忘记安装异步数据库驱动**：必须用 `asyncpg`（不是 `psycopg2`），连接串用 `postgresql+asyncpg://`
2. **Alembic 异步配置**：默认 `env.py` 是同步的，必须改写为 `run_async` 模式
3. **Windows Docker 网络**：容器间用服务名（如 `postgres`、`redis`），容器访问宿主机用 `host.docker.internal`
4. **环境变量加载**：`pydantic-settings` 自动读 `.env`，但要确保工作目录正确，建议显式指定 `env_file`
5. **开发环境 CORS**：前端在 5173，后端在 8000，CORS 必须允许 `http://localhost:5173`

## 验证标准

- `docker-compose up` 启动 postgres 和 redis 无报错
- `make dev` 启动后端服务无报错
- 访问 `localhost:8000/health` 返回 200，database 和 redis 均显示 connected
- `make test` 通过健康检查测试
- `make lint` 通过 ruff 检查
- `alembic upgrade head` 执行无报错
