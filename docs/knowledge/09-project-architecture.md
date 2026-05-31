# 项目架构总览

## 为什么分前后端

用户用浏览器访问我们的网站。浏览器只能运行 HTML/CSS/JavaScript，不能直接连数据库、不能调用 AI API。所以需要：

```
浏览器（前端 Vue）→ 发 HTTP 请求 → 服务器（后端 FastAPI）→ 查数据库、调 AI
```

前端负责**展示和交互**，后端负责**数据存储和业务逻辑**。分开的好处：
1. 前后端可以独立开发、独立部署
2. 后端代码（API Key、数据库密码）不会暴露给浏览器
3. 一个后端可以同时服务网页、手机 App、小程序

## 为什么分这么多层

```
用户请求进来
    ↓
API 层（api/articles.py）— 接收参数，调用 Service
    ↓
Service 层（services/article_service.py）— 业务逻辑（生成文章 → 评判质量 → 存储）
    ↓
┌─────────────────┐
│ Repository 层    │ — 执行 SQL（增删改查）
│（repositories/） │
└─────────────────┘
    ↕
┌─────────────────┐
│ Agent 层         │ — 调用 AI 大模型（生成内容、评判质量）
│（agents/）       │
└─────────────────┘
```

**为什么不能直接在 API 层写 SQL**：
- 如果以后要换数据库，所有 API 都要改
- 如果以后要加缓存，每个 API 都要加
- 测试时要 mock 整个数据库

分层后：API 只管接收参数，Repository 只管 SQL，Service 编排它们。改一层不影响其他层。

**为什么 Agent 单独一层**：
- LLM 调用逻辑（提示词、输出解析、重试）和业务逻辑是两回事
- Agent 可以独立测试（mock LLM 返回）
- 换 AI 模型只需要改 Agent 层

## 文件夹结构对应关系

```
backend/app/
├── api/v1/          ← API 层：定义接口（URL、参数、响应格式）
├── services/        ← Service 层：业务逻辑
├── repositories/    ← Repository 层：数据库操作
├── agents/          ← Agent 层：AI 调用
├── models/          ← 数据库表结构定义（SQLAlchemy ORM）
├── schemas/         ← 请求/响应格式定义（Pydantic）
├── config.py        ← 配置（数据库地址、API Key 等）
├── database.py      ← 数据库连接
├── main.py          ← 应用入口
├── dependencies.py  ← 共享工具（数据库连接注入）
└── exceptions.py    ← 错误类型定义
```

**models/ 和 schemas/ 为什么要分开**：
- `models/` 定义数据库表的列（id、title、password_hash）
- `schemas/` 定义 API 的请求/响应格式（返回用户信息时不包含 password_hash）
- 两者经常不一样。数据库有密码字段，API 响应不能返回密码

## 当前进度（Phase 0 完成后）

| 层 | 完成了什么 | 还没做 |
|---|---|---|
| API 层 | /health 健康检查 | 所有业务接口 |
| Service 层 | 无 | 所有业务逻辑 |
| Repository 层 | 无 | 所有数据库操作 |
| Agent 层 | 无 | 所有 AI 调用 |
| 基础设施 | 数据库连接、Redis 连接、配置管理、异常定义、迁移框架 | — |
