# 项目进度图

> 用图示展示项目"长了什么"，每个阶段完成后更新。

## 当前状态：Phase 1a-4 完成

```
你（用户）
  ↓ 浏览器
  ↓
┌─────────────────────────────────────────────────────┐
│  前端 (localhost:5173)              状态             │
│  ├── 首页 /                     ← 占位页面 ✅      │
│  ├── 文章列表 /articles         ← 占位页面 ✅      │
│  ├── 语料库 /corpus             ← 占位页面 ✅      │
│  ├── 关于 /about                ← 占位页面 ✅      │
│  └── API 客户端 (Axios)         ← 已配置 ✅        │
└────────────────────┬────────────────────────────────┘
                     ↓ Vite 代理 /api → :8000
┌────────────────────┴────────────────────────────────┐
│  后端 (localhost:8000)              状态             │
│  ├── GET /health                ← 健康检查 ✅       │
│  ├── GET /api/v1/articles       ← 文章列表 ✅       │
│  ├── GET /api/v1/articles/{id}  ← 文章详情 ✅       │
│  ├── POST /api/v1/admin/articles   ← 创建文章 ✅   │
│  ├── GET  /api/v1/admin/articles   ← 管理列表 ✅   │
│  ├── PATCH /api/v1/admin/articles/{id} ← 更新 ✅   │
│  ├── DELETE /api/v1/admin/articles/{id} ← 删除 ✅  │
│  ├── Service 层 (article_service)   ← 已创建 ✅    │
│  ├── Repository 层 (article_repo)   ← 已创建 ✅    │
│  ├── 缓存 (Redis Cache-Aside)      ← 已实现 ✅    │
│  ├── 文本工具 (text_processing)    ← 已实现 ✅    │
│  └── Agent 层 (AI)              ← 还没有 ⬜         │
├─────────────────────────────────────────────────────┤
│  数据模型                          状态             │
│  ├── articles 表                ← 已创建 ✅         │
│  ├── article_segments 表        ← 已创建 ✅         │
│  ├── users 表                   ← Phase 3 ⬜       │
│  ├── reading_sessions 表        ← Phase 2 ⬜       │
│  ├── corpus_entries 表          ← Phase 3 ⬜       │
│  └── quiz_questions 表          ← Phase 4 ⬜       │
└──────────┬──────────────────┬───────────────────────┘
           ↓                  ↓
    ┌──────────────┐   ┌──────────────┐
    │ PostgreSQL   │   │ Redis        │
    │ 2 张表 ✅    │   │ 已连接 ✅    │
    └──────────────┘   └──────────────┘
```

## 已完成的里程碑

### Phase 0a: 后端骨架 ✅
```
Python 环境 ─→ 数据库连接 ─→ Redis 连接 ─→ 健康检查 ─→ 异常体系 ─→ 测试 ─→ CI
```
- 能启动、能连数据库、能连 Redis
- `/health` 端点可用
- pytest 1 个测试通过
- GitHub Actions CI 配置好了

### Phase 0b: 前端骨架 ✅
```
Vue 项目 ─→ TailwindCSS ─→ 路由 ─→ API 客户端 ─→ Docker
```
- 4 个占位页面可访问
- Axios 客户端已配置（带 token 注入和错误处理）
- Vite 代理到后端已配置

### Phase 1a-1: 文章数据模型 ✅
```
ORM 模型 ─→ Alembic 迁移 ─→ 数据库建表 ─→ Pydantic Schemas
```
- articles 表：存文章标题、内容、难度等
- article_segments 表：存分段内容（用于分段式阅读）
- 创建和响应的数据格式已定义

### Phase 1a-2: Repository 层 ✅
```
BaseRepository ─→ ArticleRepository ─→ 17 个测试
```
- 泛型 BaseRepository：get/create/update/delete/count
- ArticleRepository：按难度/主题过滤、搜索、分页
- 测试：CRUD / 过滤 / 分页 / 搜索 / 关联查询

### Phase 1a-3: Service + API 端点 ✅
```
ArticleService ─→ 公开 API ─→ Admin API ─→ 14 个 API 测试 ─→ curl 实测
```
- 公开端点：文章列表（分页+过滤）、文章详情
- 管理端点：创建/列表/更新/删除，X-Admin-Key 认证
- Service 层：字数计算、发布状态管理
- 32 个测试全部通过

### Phase 1a-4: 缓存 + 文本工具 ✅
```
text_processing ─→ Redis 缓存 ─→ 缓存失效 ─→ 47 个测试 ─→ curl 实测
```
- 自动分段：按空行拆分，短行识别为标题
- 阅读时间：按 200 词/分钟估算
- Redis 缓存：Cache-Aside 模式，TTL 1 小时，更新/删除时自动失效
- 47 个测试全部通过，curl 全链路验证通过

## 接下来要建什么

```
Phase 1a-5: 前端文章页面 ← 下一个
  目标：用户能在浏览器看到文章列表和详情
  ┌──────────────────────────────────┐
  │  前端页面                         │
  │  ├── HomeView 文章列表（卡片）    │
  │  │   └── 标题、难度标签、字数     │
  │  └── ArticleView 文章详情        │
  │      └── 分段展示、阅读时间       │
  └──────────────────────────────────┘
```

## 最终目标（MVP 完成时）

```
用户旅程：
  注册 → 问卷定级 → 看推荐文章 → 阅读+查词辅助 → 保存到语料库 → 做理解题 → 复习

技术架构：
  浏览器 → Vue 前端 → FastAPI 后端 → PostgreSQL + Redis + 智谱AI
```
