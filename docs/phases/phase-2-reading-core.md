# Phase 2: 阅读核心

## 目标

用户可以阅读文章并获得四层辅助（词义 -> 短语 -> 句子结构 -> 段落翻译），系统追踪阅读行为。

## 前置条件

- Phase 1 完成：文章 CRUD 和 LLM 生成管线可用，文章列表和详情 API 可用
- 前端文章列表页和详情页已实现
- 数据库中已有可阅读的文章数据

## 当前进度

**已完成**: 尚未开始
**下一步**: Checkpoint 2-1 — 阅读会话数据模型（任务 2.1, 2.2, 2.3, 2.4）
**Git 分支**: `develop`

> 每个 checkpoint 完成后更新此节。新会话读此文件即可知道从哪继续。

## 检查点

### Checkpoint 2-1: 阅读会话数据模型

**包含任务：** 2.1 创建 models/reading.py, 2.2 创建 Alembic 迁移, 2.3 创建 schemas/reading.py, 2.4 创建 repositories/reading_repo.py

**Git 分支：** `feature/P2-1-reading-models`

**提交点：** 完成数据模型、迁移、Schema、Repository 后提交。

**验证命令：**
1. `alembic upgrade head` → new tables created
2. `pytest` tests for reading repository CRUD
3. `curl /health` → app still works

---

### Checkpoint 2-2: 阅读辅助 Agent

**包含任务：** 2.5 创建 agents/reading_assistant.py, 2.6 创建 agents/grammar_analyzer.py, 2.10 补充 text_processing.py, 2.12 编写 Agent 测试

**Git 分支：** `feature/P2-2-reading-agents`

**提交点：** 完成 Agent 模块和文本处理后提交。

**验证命令：**
1. `pytest` with mocked LLM → agent tests pass
2. Test each assistance type (word/phrase/sentence/paragraph)
3. Test grammar analysis output format

---

### Checkpoint 2-3: 阅读会话 API

**包含任务：** 2.7 创建 services/reading_service.py, 2.8 创建 api/v1/reading.py, 2.9 添加辅助结果缓存, 2.11 编写后端测试

**Git 分支：** `feature/P2-3-reading-api`

**提交点：** 完成服务层、API 端点、Redis 缓存和后端测试后提交。

**验证命令：**
1. `pytest` → reading service and API tests pass
2. `curl POST /api/v1/reading/sessions` → creates session, returns 201
3. `curl POST /api/v1/reading/assist` with word lookup → returns definition
4. `curl POST /api/v1/reading/assist` with same word again → faster (cache hit)
5. `curl PATCH /api/v1/reading/sessions/{id}` → updates progress
6. `curl POST /api/v1/reading/sessions/{id}/complete` → returns stats (wpm, etc.)

---

### Checkpoint 2-4: 前端阅读器组件

**包含任务：** 2.13 前端：ArticleReader.vue, 2.14 前端：辅助组件（WordTooltip, PhrasePanel, SentenceBreakdown, ParagraphTranslation）, 2.15 前端：useReadingSession, 2.16 前端：useTextSelection, 2.17 前端：useAssistance, 2.18 前端：组装阅读页

**Git 分支：** `feature/P2-4-frontend-reader`

**提交点：** 完成所有阅读器组件和组装页面后提交。

**验证命令：**
1. `npm run dev` → no errors
2. Open article → see segmented paragraphs
3. Click a word → tooltip appears with pronunciation + definition
4. Select a phrase → side panel shows explanation
5. Click sentence breakdown → expandable structure analysis
6. Click paragraph translation → collapsible translation appears
7. Scroll down → progress bar updates
8. Leave page → session completes (check Network for PATCH request)
9. F12 Console → no errors

---

### Checkpoint 2-5: E2E 测试

**包含任务：** 2.19 编写 E2E 测试

**Git 分支：** `feature/P2-5-e2e-tests`

**提交点：** 完成端到端测试后提交。

**验证命令：**
1. `npx playwright test` → E2E tests pass
2. Full flow: open article → read → select word → see definition → select phrase → see explanation → complete reading → see stats

---

## 任务清单

| # | 任务 | 复杂度 | 状态 |
|---|---|---|---|
| 2.1 | 创建 models/reading.py | 中 | ⬜ |
| 2.2 | 创建 Alembic 迁移 | 低 | ⬜ |
| 2.3 | 创建 schemas/reading.py | 中 | ⬜ |
| 2.4 | 创建 repositories/reading_repo.py | 中 | ⬜ |
| 2.5 | 创建 agents/reading_assistant.py | 高 | ⬜ |
| 2.6 | 创建 agents/grammar_analyzer.py | 高 | ⬜ |
| 2.7 | 创建 services/reading_service.py | 高 | ⬜ |
| 2.8 | 创建 api/v1/reading.py | 中 | ⬜ |
| 2.9 | 添加辅助结果缓存 | 中 | ⬜ |
| 2.10 | 补充 text_processing.py | 中 | ⬜ |
| 2.11 | 编写后端测试 | 高 | ⬜ |
| 2.12 | 编写 Agent 测试 | 中 | ⬜ |
| 2.13 | 前端：ArticleReader.vue | 高 | ⬜ |
| 2.14 | 前端：辅助组件 | 高 | ⬜ |
| 2.15 | 前端：useReadingSession | 中 | ⬜ |
| 2.16 | 前端：useTextSelection | 中 | ⬜ |
| 2.17 | 前端：useAssistance | 中 | ⬜ |
| 2.18 | 前端：组装阅读页 | 中 | ⬜ |
| 2.19 | 编写 E2E 测试 | 高 | ⬜ |

### 任务详细说明

| # | 任务 | 详细说明 |
|---|---|---|
| 2.1 | 创建 models/reading.py | ReadingSession、LookupEvent 模型。**注意：reading_sessions 表的 user_id 列设为 nullable UUID**（Phase 2 无认证时 user_id=NULL，Phase 3a 加认证后填充，避免 Phase 3 大改迁移） |
| 2.2 | 创建 Alembic 迁移 | `alembic revision --autogenerate -m "add reading session and lookup event"` |
| 2.3 | 创建 schemas/reading.py | SessionCreate/Response/Update, LookupEventCreate/Response, AssistanceRequest/Response |
| 2.4 | 创建 repositories/reading_repo.py | create_session(), get_session(), update_session(), add_lookup_event() |
| 2.5 | 创建 agents/reading_assistant.py | 统一 Agent，根据 assistance_type 切换提示词策略，处理四层辅助 |
| 2.6 | 创建 agents/grammar_analyzer.py | 分析句子结构，返回 {sentence, components: [{text, role}]} |
| 2.7 | 创建 services/reading_service.py | 会话管理（开始、更新进度、结束），计算阅读速度，聚合查词事件，调用 Assistant Agent |
| 2.8 | 创建 api/v1/reading.py | 会话管理和辅助端点 |
| 2.9 | 添加辅助结果缓存 | 词义/短语缓存，key: `assist:{hash(text)}:{type}`，TTL 24小时 |
| 2.10 | 补充 text_processing.py | 提取选中文本、获取上下文段落 |
| 2.11 | 编写后端测试 | 会话生命周期、辅助缓存、查词记录 |
| 2.12 | 编写 Agent 测试 | Mock LLM，测试每种辅助类型 |
| 2.13 | 前端：ArticleReader.vue | 主阅读组件，段落展示、文本选择、进度条 |
| 2.14 | 前端：辅助组件 | WordTooltip、PhrasePanel、SentenceBreakdown、ParagraphTranslation |
| 2.15 | 前端：useReadingSession | 管理会话状态：开始、每30s更新进度、记录查词、离开时结束 |
| 2.16 | 前端：useTextSelection | 检测文本选择、提取选中文本、判断选择类型（词/短语/句子） |
| 2.17 | 前端：useAssistance | 调用辅助 API、管理加载状态、客户端缓存结果 |
| 2.18 | 前端：组装阅读页 | ReadingView.vue 组合所有组件 |
| 2.19 | 编写 E2E 测试 | Playwright：打开文章 -> 阅读 -> 选词 -> 看释义 -> 选短语 -> 看解释 -> 完成 |

## API 端点

```
POST /api/v1/reading/sessions
  认证：无（Phase 3a 加认证）
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

## 数据模型变更

### reading_sessions

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | UUID | PK | |
| user_id | UUID | FK users(id), **NULLABLE** | Phase 2 无认证时为 NULL，Phase 3a 加认证后填充 |
| article_id | UUID | FK articles(id) | |
| started_at | TIMESTAMPTZ | NOT NULL | |
| ended_at | TIMESTAMPTZ | | |
| total_duration_seconds | INTEGER | | 活跃阅读时间 |
| words_looked_up | INTEGER | default 0 | 查词次数 |
| segments_read | INTEGER | default 0 | |
| completion_percentage | FLOAT | default 0 | |
| created_at | TIMESTAMPTZ | default now() | |

索引：`(user_id, started_at)`, `(user_id, article_id)`

### lookup_events

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | UUID | PK | |
| session_id | UUID | FK reading_sessions(id) CASCADE | |
| segment_index | INTEGER | | |
| selected_text | TEXT | NOT NULL | |
| lookup_type | VARCHAR(20) | NOT NULL | 'word'/'phrase'/'sentence'/'paragraph' |
| result_snapshot | JSONB | | 辅助结果快照 |
| created_at | TIMESTAMPTZ | default now() | |

## 设计模式

1. **策略模式**（辅助类型）：ReadingAssistantAgent 内部根据 assistance_type 选择不同提示词模板和输出解析器
2. **观察者模式**（阅读事件）：查词事件作为副效应异步记录，不影响辅助响应速度
3. **Composable 模式**（前端）：useReadingSession、useTextSelection、useAssistance 封装有状态逻辑

## 并发考虑

- **辅助请求频繁**：用户点击多个词。Redis 缓存是第一道防线，常见词几乎总是缓存命中
- **客户端防抖**：前端 300ms 防抖，用户快速切换选择时取消前一个请求
- **进度更新限流**：Redis 记录上次更新时间，15秒内跳过重复更新
- **句子/段落分析限并发**：Semaphore 限制同时 3 个高成本 LLM 调用

## 测试要求

| 层 | 测试内容 | 方式 |
|---|---|---|
| Agent 单元 | ReadingAssistantAgent 产出有效 JSON | Mock openai.ChatCompletion.create，测试四种辅助类型 |
| Agent 单元 | GrammarAnalyzer 语法分析 | Mock LLM，测试结构解析输出 |
| Service | 会话生命周期 | Mock Repository 和 Agent，测试开始、更新、完成流程 |
| Service | 阅读速度计算 | 测试 WPM 计算逻辑 |
| Repository | 会话和查词 CRUD | 测试数据库，增删改查、关联查询 |
| API | 端点 | httpx.AsyncClient，测试会话创建、进度更新、辅助请求、查词记录 |
| E2E | 完整阅读流程 | Playwright：打开文章 -> 阅读 -> 选词 -> 看释义 -> 完成 |

## 陷阱

1. **跨段落文本选择**：用户可能选中跨两段的内容，前端需处理这种情况
2. **阅读时间不准确**：用活跃阅读时间（页面可见+近期滚动），而非起止时间差
3. **辅助面板遮挡文本**：窄屏用底部抽屉，宽屏用侧边栏，必须从开始就设计响应式
4. **LLM 编造释义**：系统提示词中要求只用标准词典定义，不确定时说"未找到释义"
5. **用户关闭页面丢进度**：用 beforeunload 发送最终进度更新，同时每 30s 自动保存
6. **user_id 可空**：reading_sessions 的 user_id 必须设为 nullable，Phase 2 阶段该字段全部为 NULL

## 验证标准

- 打开文章 -> 点击单词看到释义 -> 展开段落翻译 -> 完成阅读看到统计
- Redis 缓存命中时辅助响应 < 50ms
- 四层辅助（词义、短语、句子、段落）全部正常工作
- 阅读会话正确记录：开始时间、进度更新、查词次数、完成百分比、阅读速度
- 前端响应式：窄屏辅助面板在底部，宽屏在侧边
- E2E 测试通过完整阅读流程
