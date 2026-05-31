# 知识库

基于项目实际代码编写的知识文件。每个文件回答：**为什么需要它**、**它是什么**、**怎么用**。

> 建议先看 00-full-flow 了解全貌，再按需看具体主题。

## 基础概念

| 文件 | 主题 |
|---|---|
| [00-full-flow.md](00-full-flow.md) | **先看这个** — 一个请求从浏览器到响应的完整链路 |
| [06-async-explained.md](06-async-explained.md) | 异步编程 — 为什么 Web 服务器需要 async/await |

## 后端核心

| 文件 | 主题 |
|---|---|
| [04-decorators-and-routing.md](04-decorators-and-routing.md) | 装饰器与路由 — `@app.get` 为什么这样写、GET/POST 区别 |
| [05-app-state-and-lifespan.md](05-app-state-and-lifespan.md) | app.state 和 lifespan — 应用启动/关闭管理 |
| [07-dependency-injection-explained.md](07-dependency-injection-explained.md) | 依赖注入 — Depends() 工作原理 |
| [08-pydantic-settings-explained.md](08-pydantic-settings-explained.md) | 配置管理 — .env 和 config.py 的关系 |

## 数据与存储

| 文件 | 主题 |
|---|---|
| [02-postgresql-and-redis.md](02-postgresql-and-redis.md) | 两个数据库 — PostgreSQL vs Redis、连接串、连接池 |
| [03-alembic-and-migrations.md](03-alembic-and-migrations.md) | 数据库迁移 — 为什么不能手动建表 |

## 前端与通信

| 文件 | 主题 |
|---|---|
| [11-frontend-basics.md](11-frontend-basics.md) | **前端入门** — Vue/Vite/Axios 是什么、.vue 文件结构、前后端数据流通 |
| [10-api-and-frontend-backend.md](10-api-and-frontend-backend.md) | API 设计与前后端通信 — 接口规划、Vite 代理、Axios 拦截器、前端路由 |

## 架构与规范

| 文件 | 主题 |
|---|---|
| [09-project-architecture.md](09-project-architecture.md) | 项目架构 — 为什么要分层、文件夹结构对应关系 |
| [01-docker-and-containers.md](01-docker-and-containers.md) | Docker — 容器化开发环境 |

## 后续补充计划

| 阶段 | 待补充主题 |
|---|---|
| Phase 1 | ORM 模型（SQLAlchemy）、Repository 模式、LLM Agent |
| Phase 2 | Vue 组件、Composition API |
| Phase 3 | JWT 认证、bcrypt 密码哈希、FSRS 间隔重复 |
| Phase 4 | 测试策略、CI/CD |
