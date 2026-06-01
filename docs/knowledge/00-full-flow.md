# 项目进度图

> 用图示展示项目"长了什么"，每个阶段完成后更新。

## 当前状态：Phase 1b-1 完成（LLM 基础设施）

```
你（用户）
  ↓ 浏览器
  ↓
┌─────────────────────────────────────────────────────┐
│  前端 (localhost:5173)              状态             │
│  ├── 首页 / 文章列表             ← 卡片列表 ✅      │
│  ├── 文章详情 /articles/:id      ← 分段展示 ✅      │
│  ├── 语料库 /corpus             ← 占位页面 ⬜      │
│  ├── 关于 /about                ← 占位页面 ✅      │
│  ├── API 客户端 (Axios)         ← 已配置 ✅        │
│  └── Composable (useArticles)   ← 状态管理 ✅      │
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
│  ├── LLM Client (llm_client)      ← 已实现 ✅    │
│  ├── BaseAgent (agents/base)       ← 已实现 ✅    │
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
    │ 2 张表 ✅    │   │ 缓存+队列 ✅ │
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

### Phase 1a: 文章 CRUD（全链路）✅
```
数据模型 ─→ Repository ─→ Service ─→ API ─→ 缓存 ─→ 文本工具 ─→ 前端页面
  1a-1       1a-2        1a-3      1a-3    1a-4      1a-4        1a-5
```
- 6 个 API 端点：列表、详情、创建、管理列表、更新、删除
- Admin Key 认证、分页、按难度/主题过滤
- Redis 缓存（Cache-Aside，TTL 1 小时）
- 自动分段（heading 检测）、字数统计、阅读时间估算
- 前端：文章卡片列表 + 分段详情页
- 47 个后端测试全部通过

### Phase 1b-1: LLM 基础设施 ✅
```
LLMClient ─→ BaseAgent ─→ JSON 解析+重试 ─→ 12 个测试
```
- LLMClient：封装 OpenAI SDK，指数退避重试（1s→2s→4s），日志记录 token 用量
- BaseAgent：system_prompt 管理，JSON→Pydantic 校验，解析失败自动重试+错误提示注入
- 59 个测试全部通过

## 接下来要建什么

```
Phase 1b-2: 内容生成管线 ← 下一个
  目标：两个 AI Agent 协作，自动生成+评判文章
  ┌──────────────────────────────────┐
  │  ContentGenerator（写手）        │
  │  └── 输入 topic/difficulty       │
  │      输出 {title, segments, ...} │
  │              ↓                   │
  │  ContentJudge（评委）            │
  │  └── 评分 0-1，低于 0.7 则重试   │
  │              ↓                   │
  │  Service 层编排（管线）          │
  │  └── 生成 → 评判 → 重试/存储    │
  └──────────────────────────────────┘
```

## 最终目标（MVP 完成时）

```
用户旅程：
  注册 → 问卷定级 → 看推荐文章 → 阅读+查词辅助 → 保存到语料库 → 做理解题 → 复习

技术架构：
  浏览器 → Vue 前端 → FastAPI 后端 → PostgreSQL + Redis + 智谱AI
```
