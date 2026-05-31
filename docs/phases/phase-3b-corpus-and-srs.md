# Phase 3b: 语料库与间隔复习

## 目标

实现个人语料库（保存/复习/导出）、FSRS 间隔复习、简单标签难度匹配推荐。阅读时查词可自动保存到语料库。

## 前置条件

- Phase 3a 完成：用户认证可用，阅读会话已关联 user_id
- reading_sessions 的 user_id 已通过认证填充
- 前端认证页面和路由守卫已实现

## 当前进度

**已完成**: 尚未开始
**下一步**: Checkpoint 3b-1 — 语料库数据模型与 CRUD（任务 3b.1, 3b.2, 3b.3, 3b.4, 3b.5）
**Git 分支**: `develop`

> 每个 checkpoint 完成后更新此节。新会话读此文件即可知道从哪继续。

## 检查点与 Git 提交点

### Checkpoint 3b-1: 语料库数据模型与 CRUD

**涵盖任务**: 3b.1, 3b.2, 3b.3, 3b.4, 3b.5
**Git 分支**: `feature/P3b-1-corpus-model`

**提交时机**: corpus 模型、迁移、schemas、corpus_repo、corpus_service 全部完成后提交

**验证命令**:
1. `alembic upgrade head` → corpus_entries 和 review_log 表创建成功
2. `pytest` → 语料库 CRUD 测试通过（创建、读取、更新、删除、去重检测）

---

### Checkpoint 3b-2: FSRS 间隔复习

**涵盖任务**: 3b.6, 3b.7
**Git 分支**: `feature/P3b-2-fsrs-review`

**提交时机**: FSRS 集成、srs_service、语料库复习端点全部完成后提交

**验证命令**:
1. `pytest` → FSRS 复习周期测试通过
2. `curl POST /api/v1/corpus` → 创建条目 → 状态码 201
3. `curl GET /api/v1/corpus/reviews/due` → 显示到期复习项目
4. `curl POST /api/v1/corpus/{id}/review -d '{"rating":3}'` → 更新 next_review 日期
5. 同一词条评分 rating=1 (Again) → next_review 比 rating=4 (Easy) 更早

---

### Checkpoint 3b-3: 推荐与导出

**涵盖任务**: 3b.8, 3b.9
**Git 分支**: `feature/P3b-3-recommendation-export`

**提交时机**: 简单推荐服务、推荐端点、语料库导出全部完成后提交

**验证命令**:
1. `curl GET /api/v1/articles/recommended` → 返回匹配用户水平和兴趣的文章
2. 阅读一篇文章 → 再次请求推荐 → 该文章被排除
3. `curl GET /api/v1/corpus/export?format=json` → 下载 JSON 文件
4. `curl GET /api/v1/corpus/export?format=csv` → 下载 CSV 文件

---

### Checkpoint 3b-4: 前端语料库与复习页面

**涵盖任务**: 3b.10, 3b.11, 3b.12, 3b.13, 3b.14
**Git 分支**: `feature/P3b-4-frontend-corpus`

**提交时机**: 语料库页面、复习闪卡页、导出按钮、阅读时自动保存全部完成后提交

**验证命令**:
1. `npm run dev` → 无报错
2. 阅读文章 → 点击某个词的"保存到语料库" → 出现在语料库页面
3. 访问 /corpus → 看到已保存条目，按类型过滤正常
4. 在语料库中搜索 → 结果实时更新
5. 点击"复习" → 显示闪卡，评分 Again/Hard/Good/Easy → 出现下一张卡片
6. 点击"导出" → 下载文件
7. F12 控制台 → 无报错

---

## 任务清单

| # | 任务 | 复杂度 | 状态 |
|---|---|---|---|
| 3b.1 | 创建 models/corpus.py | 中 | ⬜ |
| 3b.2 | 创建迁移 | 低 | ⬜ |
| 3b.3 | 创建 schemas/corpus.py | 中 | ⬜ |
| 3b.4 | 创建 repositories/corpus_repo.py | 中 | ⬜ |
| 3b.5 | 创建 services/corpus_service.py | 高 | ⬜ |
| 3b.6 | 集成 FSRS 库 | 高 | ⬜ |
| 3b.7 | 创建 api/v1/corpus.py | 中 | ⬜ |
| 3b.8 | 创建 recommendation_service.py | 低 | ⬜ |
| 3b.9 | 更新 articles.py | 低 | ⬜ |
| 3b.10 | 编写语料库测试 | 高 | ⬜ |
| 3b.11 | 前端：语料库页面 | 高 | ⬜ |
| 3b.12 | 前端：复习页 | 高 | ⬜ |
| 3b.13 | 前端：导出功能 | 低 | ⬜ |
| 3b.14 | 阅读会话自动保存到语料库 | 中 | ⬜ |

### 任务详细说明

| # | 任务 | 详细说明 |
|---|---|---|
| 3b.1 | 创建 models/corpus.py | CorpusEntry、ReviewLog 模型，见下方数据模型 |
| 3b.2 | 创建迁移 | `alembic revision --autogenerate -m "add corpus entries and review log"` |
| 3b.3 | 创建 schemas/corpus.py | CorpusEntryCreate/Response/Update, ReviewSubmitRequest/Response, ExportRequest |
| 3b.4 | 创建 repositories/corpus_repo.py | CRUD + find_duplicate(), get_due_reviews(), get_by_user() |
| 3b.5 | 创建 services/corpus_service.py | 保存（查重+初始SRS状态）、查询、更新、删除、导出（CSV/JSON） |
| 3b.6 | 集成 FSRS 库 | 安装 fsrs 包（4.0+），创建 services/srs_service.py 封装算法。核心概念：Card、Rating、ReviewLog、Scheduler |
| 3b.7 | 创建 api/v1/corpus.py | 语料库 CRUD + 复习端点 + 导出端点 |
| 3b.8 | 创建 recommendation_service.py | **MVP 简化版**：纯标签难度匹配 + 排除已读文章。不实现高级算法（排除已读+优先未知词汇等），Phase 5+ 再升级。逻辑：根据用户 level 匹配文章 difficulty，根据用户 interests 匹配 topic，排除该用户已读过的文章（通过 reading_sessions 表判断） |
| 3b.9 | 更新 articles.py | 添加 GET /articles/recommended（需认证），调用 recommendation_service |
| 3b.10 | 编写语料库测试 | CRUD、去重（唯一约束）、FSRS 复习周期、导出（CSV/JSON 格式验证） |
| 3b.11 | 前端：语料库页面 | CorpusView：按类型过滤、搜索、分页，从阅读页一键保存 |
| 3b.12 | 前端：复习页 | 闪卡式复习：显示词条 -> 用户评分(Again/Hard/Good/Easy) -> 显示答案 -> 下一张 |
| 3b.13 | 前端：导出功能 | 下载 CSV/JSON。调用 GET /api/v1/corpus/export，触发浏览器文件下载 |
| 3b.14 | 阅读会话自动保存到语料库 | 更新阅读辅助流程：查词后提供"保存到语料库"按钮，调用 POST /api/v1/corpus 保存。自动填充 entry_type（根据 lookup_type）、content、context、context_source_id |

## API 端点

```
GET /api/v1/corpus
  认证：Bearer token
  查询参数：entry_type, search, sort, order, page, page_size
  响应 200: { "items": [{ "id", "entry_type", "content", "context", "translation",
              "review_count", "next_review", ... }], "total", "page" }

POST /api/v1/corpus
  认证：Bearer token
  请求体：{ "entry_type", "content", "context", "source_article_id",
            "translation", "definition", "cefr_level" }
  响应 201: 完整条目
  响应 409: {"detail": "Entry already exists in corpus"}

DELETE /api/v1/corpus/{entry_id}
  认证：Bearer token（必须拥有该条目）
  响应 204

GET /api/v1/corpus/reviews/due
  认证：Bearer token
  查询参数：limit(default 20), entry_type
  响应 200: { "items": [...], "total_due", "returned" }

POST /api/v1/corpus/{entry_id}/review
  认证：Bearer token
  请求体：{ "rating": 3 }  // 1=Again, 2=Hard, 3=Good, 4=Easy
  响应 200: { "next_review", "srs_interval_days", "review_count" }

GET /api/v1/corpus/export
  认证：Bearer token
  查询参数：format(csv|json), entry_type
  响应 200: 文件下载（Content-Disposition: attachment）

GET /api/v1/articles/recommended
  认证：Bearer token
  查询参数：limit(default 5)
  响应 200: { "articles": [{..., "match_reason": "..."}] }
```

## 数据模型变更

### corpus_entries

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | UUID | PK | |
| user_id | UUID | FK users(id) CASCADE | |
| entry_type | VARCHAR(20) | NOT NULL | 'word'/'phrase'/'chunk'/'sentence'/'grammar_point' |
| content | TEXT | NOT NULL | 词条内容 |
| context | TEXT | | 原文上下文 |
| context_source_id | UUID | FK articles(id) NULL | 来源文章 |
| context_segment_index | INTEGER | | 来源段落 |
| translation | TEXT | | 母语翻译 |
| definition | TEXT | | 英文释义 |
| cefr_level | VARCHAR(4) | | |
| srs_data | JSONB | default '{}' | FSRS 状态 |
| next_review | TIMESTAMPTZ | | 下次复习时间 |
| review_count | INTEGER | default 0 | |
| created_at | TIMESTAMPTZ | default now() | |
| updated_at | TIMESTAMPTZ | default now() | |

索引：`(user_id)`, `(user_id, entry_type)`, `(user_id, next_review) WHERE next_review IS NOT NULL`, `(user_id, content)` 用于去重

**唯一约束**：`UNIQUE (user_id, entry_type, content)` 防止用户重复保存

### review_log

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | UUID | PK | |
| corpus_entry_id | UUID | FK corpus_entries(id) CASCADE | |
| rating | SMALLINT | NOT NULL, CHECK (1-4) | 1=Again, 2=Hard, 3=Good, 4=Easy |
| state | JSONB | | FSRS 状态快照 |
| reviewed_at | TIMESTAMPTZ | default now() | |

## 设计模式

1. **值对象（SRS 状态）**：FSRS 卡片状态用 Pydantic 模型（SRSState）序列化到 JSONB
2. **工厂方法（语料条目）**：不同 entry_type 有不同创建逻辑（词自动获取释义，短语自动获取搭配）
3. **Facade（推荐服务）**：简单的标签匹配逻辑，封装为独立服务，Phase 5+ 可替换为高级算法

### 简化推荐算法逻辑

```
recommendation_service.py:
1. 获取用户 level 和 interests（从 UserPreference）
2. 查询已发布文章，按 difficulty 匹配 level
3. 按 topic 匹配 interests（有交集的优先）
4. 排除该用户已读过的文章（reading_sessions 中有记录的）
5. 返回 top N（默认 5）+ match_reason 说明
```

## 测试要求

| 层 | 测试内容 | 方式 |
|---|---|---|
| 单元 | srs_service：FSRS 调度 | 测试不同 rating 对 next_review 的影响 |
| 单元 | corpus_service：查重 | 测试相同 content 返回冲突 |
| 单元 | corpus_service：导出 | 测试 CSV 和 JSON 输出格式 |
| 单元 | recommendation_service：推荐 | Mock Repository，测试难度匹配、已读排除 |
| Service | 语料库 CRUD | 完整创建、查询、更新、删除流程 |
| Service | 复习流程 | 提交评分 -> 更新 SRS 状态 -> 记录 review_log |
| API | 语料库端点 | httpx.AsyncClient，测试 CRUD、复习、导出 |
| API | 导出格式 | 测试 CSV 和 JSON 下载响应的 Content-Type 和内容 |
| API | 推荐端点 | 测试认证用户获取推荐、未认证返回 401 |

## 陷阱

1. **FSRS 集成**：仔细读 fsrs 库文档，核心概念是 Card、Rating、ReviewLog、Scheduler。不要自己造 SRS 轮子
2. **语料库无限增长**：500 条时软提示"先复习再添加"，不硬性阻止
3. **忘记关联来源文章**：context_source_id 对"在上下文中复习"功能至关重要
4. **语料去重**：数据库唯一约束 `(user_id, entry_type, content)` 防止并发保存重复
5. **FSRS 状态更新原子性**：复习时 FSRS 状态更新和 review_log 创建必须在同一事务中
6. **复习批处理**：前端批量发送复习结果（每 10 个一批），避免 50 个卡片 50 次 API 调用
7. **推荐算法保持简单**：MVP 只做标签匹配 + 排除已读，不实现"优先未知词汇"等复杂逻辑
8. **导出功能编码**：CSV 导出注意 UTF-8 BOM 头，确保中文正确显示

## 验证标准

- 从阅读页查词后可一键保存到语料库
- 语料库页面支持按类型过滤、搜索、分页
- 重复保存同一词条返回 409 冲突
- FSRS 复习：提交评分后 next_review 时间正确更新
- 到期复习列表正确返回 next_review <= now() 的条目
- 导出 CSV 和 JSON 功能正常，内容完整
- 推荐文章匹配用户水平、排除已读
- 前端闪卡复习流程：显示词条 -> 评分 -> 翻转答案 -> 下一张
