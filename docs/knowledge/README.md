# 知识库

基于项目实际代码编写的知识文件。每个文件回答：**为什么需要它**、**它是什么**、**怎么用**。

## 目录

| 文件 | 主题 |
|---|---|
| [00-full-flow.md](00-full-flow.md) | **先看这个** — 一个请求从浏览器到响应的完整链路，每个环节对应什么文件 |
| [01-docker-and-containers.md](01-docker-and-containers.md) | Docker — 为什么用、镜像/容器/数据卷是什么 |
| [02-postgresql-and-redis.md](02-postgresql-and-redis.md) | 两个数据库 — 为什么用两个、连接串怎么看 |
| [03-alembic-and-migrations.md](03-alembic-and-migrations.md) | 数据库迁移 — 为什么不能手动建表、迁移怎么用 |
| [04-decorators-and-routing.md](04-decorators-and-routing.md) | 装饰器 — 为什么 `@app.get` 这样写、GET/POST 区别 |
| [05-app-state-and-lifespan.md](05-app-state-and-lifespan.md) | app.state 和 lifespan — 为什么这样写、怎么串起来的 |
| [06-async-explained.md](06-async-explained.md) | 异步 — 为什么 Web 服务器需要异步、async/await 怎么用 |
| [07-dependency-injection-explained.md](07-dependency-injection-explained.md) | 依赖注入 — Depends 怎么工作、为什么不用全局变量 |
| [08-pydantic-settings-explained.md](08-pydantic-settings-explained.md) | 配置管理 — .env 和 config.py 的关系、优先级 |

## 后续补充计划

| 阶段 | 待补充主题 |
|---|---|
| Phase 1 | ORM 模型（SQLAlchemy）、Repository 模式、LLM Agent |
| Phase 2 | Vue 组件、Composition API |
| Phase 3 | JWT 认证、bcrypt 密码哈希、FSRS 间隔重复 |
| Phase 4 | 测试策略、CI/CD |
