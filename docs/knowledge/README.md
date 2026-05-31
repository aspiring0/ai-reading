# 知识库

基于项目实际代码编写的知识文件，解释开发过程中遇到的技术概念。

> 按项目进度持续补充。每个文件都结合项目中的真实代码来解释，不是泛泛而谈。

## 目录

| 文件 | 主题 | 涵盖内容 |
|---|---|---|
| [01-docker-and-containers.md](01-docker-and-containers.md) | Docker 容器化 | image, container, ports, volumes, healthcheck, docker compose 命令 |
| [02-postgresql-and-redis.md](02-postgresql-and-redis.md) | 数据库与缓存 | 为什么同时用两个数据库、连接串、连接池、Redis 操作示例 |
| [03-alembic-and-migrations.md](03-alembic-and-migrations.md) | 数据库迁移 | 迁移是什么、为什么需要、异步 env.py、autogenerate 机制 |
| [04-fastapi-request-lifecycle.md](04-fastapi-request-lifecycle.md) | FastAPI 请求流程 | 请求生命周期、lifespan、CORS、app.state、路由挂载 |
| [05-async-python-patterns.md](05-async-python-patterns.md) | 异步编程 | async/await、同步 vs 异步、get_db 的 yield 模式、什么时候用 async |
| [06-dependency-injection.md](06-dependency-injection.md) | 依赖注入 | Depends() 工作原理、嵌套依赖、Request 对象、request.app.state |
| [07-pydantic-and-config.md](07-pydantic-and-config.md) | 配置管理 | pydantic-settings、优先级、@property、单例模式 |

## 后续计划

以下主题会在对应 Phase 开发时补充：

| 阶段 | 待补充主题 |
|---|---|
| Phase 1 | ORM 模型与 SQLAlchemy 2.0、Repository 模式、LLM Agent 基类 |
| Phase 2 | WebSocket / SSE（如果需要实时辅助）、前端 Composition API |
| Phase 3 | JWT 认证原理、bcrypt 密码哈希、FSRS 间隔重复算法 |
| Phase 4 | 测试策略（mock vs 真实数据库）、CI/CD 工作流 |
