# Phase 1b: LLM 内容生成管线

## 目标

在 Phase 1a 的 CRUD 基础上，接入 LLM 智能体实现文章自动生成和质量评判。构建完整的生成管线：生成 Agent 产出文章 → 评判 Agent 评分 → 达标则存储，不达标则带反馈重试。阶段结束后管理员可通过 API 触发文章生成并获取结果。

## 前置条件

- Phase 1a（文章模型与 CRUD）已完成
- 文章 CRUD API 全部可用，测试通过
- Redis 缓存正常工作
- `OPENAI_API_KEY` 和 `OPENAI_BASE_URL` 已在 `.env` 中配置
- `backend/app/repositories/article_repo.py`、`services/article_service.py` 已就绪

## 检查点

### Checkpoint 1b-1: LLM 基础设施
**任务**: 创建 utils/llm_client.py, agents/base.py
**Git 分支**: `feature/P1b-1-llm-infrastructure`
**Git commit**: `feat(llm): add async LLM client wrapper and BaseAgent class`

验证步骤：
1. `pytest tests/test_llm/` — LLM client 和 BaseAgent 单元测试通过
2. `python -c "from app.utils.llm_client import LLMClient; from app.agents.base import BaseAgent; print('imports OK')"` — 模块导入正常
3. `pytest -k "llm_client" -v` — 测试指数退避重试、超时处理、JSON 解析逻辑
4. `pytest -k "base_agent" -v` — 测试 system_prompt 管理、重试逻辑、错误处理
5. 确认 `OPENAI_API_KEY` 和 `OPENAI_BASE_URL` 可从 `.env` 加载：`python -c "from app.config import settings; print(settings.OPENAI_BASE_URL)"`

### Checkpoint 1b-2: 内容生成管线（Agent + Pipeline）
**任务**: 创建 agents/content_generator.py, agents/content_judge.py, 更新 services/article_service.py 添加管线编排
**Git 分支**: `feature/P1b-2-generation-pipeline`
**Git commit**: `feat(agents): add ContentGenerator, ContentJudge agents and pipeline orchestration`

验证步骤：
1. `pytest tests/test_agents/` — ContentGenerator 和 ContentJudge 单元测试通过
2. `pytest -k "pipeline" -v` — 管线编排测试通过（正常路径 + 重试路径）
3. Mock Judge 返回低分 → 验证最多重试 2 次（共 3 次尝试），不无限循环
4. Mock Generator 返回无效 JSON → 验证重试逻辑和错误处理正常
5. `python -c "from app.agents.content_generator import ContentGenerator; from app.agents.content_judge import ContentJudge; print('agents import OK')"` — 模块导入正常
6. 管线完成后 `generation_metadata` 包含 model、token 用量、生成尝试次数

### Checkpoint 1b-3: 生成 API 端点
**任务**: 添加 POST generate 端点, GET generation-status 端点
**Git 分支**: `feature/P1b-3-generation-api`
**Git commit**: `feat(api): add article generation and status polling endpoints`

验证步骤：
1. `pytest tests/test_api/test_generation.py` — 生成 API 测试通过
2. 启动 uvicorn → `curl http://localhost:8000/docs` — 能看到 generate 和 generation-status 端点
3. `curl -X POST http://localhost:8000/api/v1/admin/articles/generate -H "Content-Type: application/json" -H "X-Admin-Key: test" -d '{"topic":"climate change","difficulty":"intermediate","target_word_count":400}'` — 返回 202 + task_id
4. `curl http://localhost:8000/api/v1/admin/articles/generation-status/{task_id} -H "X-Admin-Key: test"` — 返回状态（processing/completed/failed）
5. 无 X-Admin-Key 时调用 → 返回 401/403
6. 不存在的 task_id → `curl http://localhost:8000/api/v1/admin/articles/generation-status/nonexistent -H "X-Admin-Key: test"` — 返回 404
7. `redis-cli KEYS "gen_task:*"` — 能看到任务状态缓存 key

### Checkpoint 1b-4: 测试 + 前端管理生成页
**任务**: 编写完整 Mock LLM 测试, 前端管理生成页（表单 + 状态轮询）
**Git 分支**: `feature/P1b-4-tests-and-admin-ui`
**Git commit**: `feat(ui): add admin generation page with polling and complete test suite`

验证步骤：
1. `pytest tests/ -v` — 全部测试通过（Agent 单元、Service 管线、API 端点、集成测试）
2. `pytest -k "mock" -v` — Mock LLM 测试覆盖：正常生成、评判拒绝重试、JSON 解析失败、超时处理
3. `npm run dev` → 浏览器打开管理页 — 看到生成表单（主题输入、难度选择、目标字数、生成按钮）
4. 填写表单点击生成 → 显示 processing 状态，轮询更新进度
5. 生成完成后显示结果（quality_score、article_id），可点击跳转到文章详情
6. 生成失败时显示错误信息
7. F12 Network — 能看到 `POST /generate` (202) 和 `GET /generation-status` 轮询请求

## 任务清单

| # | 任务 | 复杂度 | 状态 |
|---|---|---|---|
| 1b.1 | 创建 `utils/llm_client.py` — 封装 openai.AsyncOpenAI，配置 base_url，指数退避重试，超时处理 | 中 | ⬜ |
| 1b.2 | 创建 `agents/base.py` — BaseAgent 类：system_prompt 管理、LLM 调用、JSON 解析、重试逻辑、错误处理 | 中 | ⬜ |
| 1b.3 | 创建 `agents/content_generator.py` — 内容生成 Agent，返回结构化 JSON：{title, segments, word_count, cefr_level} | 高 | ⬜ |
| 1b.4 | 创建 `agents/content_judge.py` — 质量评判 Agent，多维度评分（语法、词汇、连贯性、吸引力），低于阈值则拒绝 | 高 | ⬜ |
| 1b.5 | 更新 `services/article_service.py` — 添加生成管线编排逻辑：生成 → 评判 → 不达标重试（最多 2 次） → 存储 | 高 | ⬜ |
| 1b.6 | 添加 `POST /api/v1/admin/articles/generate` 端点 — 异步触发生成，返回 202 + task_id | 中 | ⬜ |
| 1b.7 | 添加 `GET /api/v1/admin/articles/generation-status/{task_id}` 端点 — 查询生成任务状态 | 中 | ⬜ |
| 1b.8 | 编写测试 — Mock LLM 响应，测试完整管线含重试逻辑、Agent 单元、API 端点 | 高 | ⬜ |
| 1b.9 | 前端：管理生成页 — 表单：主题输入、难度选择、目标字数、生成按钮、状态轮询 | 低 | ⬜ |

## API 端点

### 管理生成端点（新增）

```
POST /api/v1/admin/articles/generate
  认证：Admin API Key (X-Admin-Key header)
  请求体：
    { "topic": "climate change", "difficulty": "intermediate",
      "target_word_count": 400, "custom_instructions": "..." }
  响应 202:
    { "task_id": "uuid", "status": "processing" }

GET /api/v1/admin/articles/generation-status/{task_id}
  认证：Admin API Key
  响应 200:
    { "task_id", "status": "completed"|"processing"|"failed",
      "article_id", "quality_score", "generation_attempts", "error" }
```

### 说明

- `POST /generate` 返回 `202 Accepted`，文章生成在后台任务中执行（MVP 使用 FastAPI BackgroundTasks）
- 生成任务状态存储在 Redis 中（key: `gen_task:{task_id}`），设置 TTL（如 1 小时）
- 前端通过轮询 `generation-status` 端点获取进度
- 生成完成后，`article_id` 填入状态，前端可直接跳转到文章详情

## 数据模型变更

无新增表。本阶段使用 Phase 1a 已创建的 `articles` 表，填充以下之前为 NULL 的字段：

| 字段 | 填充时机 | 内容 |
|---|---|---|
| `quality_score` | 评判 Agent 评分后 | 0-1 的浮点数 |
| `generation_metadata` | 生成完成后 | 使用的 prompt、模型名、token 用量、生成尝试次数 |

## 设计模式

### Agent 设计

1. **BaseAgent 类**（`agents/base.py`）：
   - 所有 LLM Agent 的基类
   - 管理 system_prompt 模板
   - 封装 LLM 调用：调用 `llm_client`、解析 JSON 响应、重试逻辑
   - 返回类型化的 Result 对象（Pydantic 模型），而非原始字符串
   - 错误处理：JSON 解析失败重试、超时处理

2. **ContentGenerator Agent**（`agents/content_generator.py`）：
   - 继承 BaseAgent
   - 接收参数：topic, difficulty, target_word_count, custom_instructions
   - 让 LLM 直接生成分段结构（段落数组），**不要事后分段**（事后分段效果差）
   - 返回结构化结果：`{title, segments: [{segment_index, segment_type, content}], word_count, cefr_level}`

3. **ContentJudge Agent**（`agents/content_judge.py`）：
   - 继承 BaseAgent
   - 接收生成的文章内容，多维度评分：语法正确性、词汇多样性、连贯性、吸引力
   - 返回评分结果：`{score: float, dimensions: {...}, passed: bool, feedback: string}`
   - 低于阈值（如 0.7）则 `passed=False`，附带改进建议

### Pipeline 模式（生成管线）

```
ContentGenerator Agent
        │
        ▼
ContentJudge Agent
        │
   ┌────┴────┐
   │ passed? │
   └────┬────┘
    yes │     no (≤ 2 次重试)
        │      │
        ▼      ▼ (带 feedback 重新生成)
    存储文章    回到 ContentGenerator
        │
        ▼
   更新 Redis task 状态 → completed
```

- 每步独立可扩展，后续可插入更多 Agent（如风格检查）
- 最大重试 2 次（共 3 次尝试），仍不达标则存储最后一次结果并标记低质量
- 保存生成元数据：prompt、模型名、token 用量到 `generation_metadata`

### 并发考虑

- **文章生成是慢操作**（5-30 秒），不能阻塞 API 响应。返回 `202 Accepted` + task_id，后台任务处理
- **后台任务**：MVP 用 FastAPI BackgroundTasks（同进程），生产环境迁移到 Celery/ARQ
- **LLM 限流**：OpenAI SDK 内置重试 + 指数退避，额外加 `asyncio.Semaphore(5)` 限制并发 LLM 调用
- **任务状态存储**：用 Redis 存储 task 状态（key: `gen_task:{task_id}`），设置 TTL。服务器重启时 BackgroundTasks 会丢失，通过 Redis 状态手动恢复

## 测试要求

| 层 | 测试内容 | 方式 |
|---|---|---|
| Agent 单元 | ContentGenerator 产出有效 JSON | Mock `openai.ChatCompletion.create` |
| Agent 单元 | ContentJudge 评分逻辑 — 低于阈值拒绝、JSON 格式错误 | Mock LLM |
| Service | 生成管线编排 — 正常路径、重试路径、最大重试后仍失败 | Mock 两个 Agent |
| API | 生成端点返回 202、状态轮询 completed/failed、404 | httpx.AsyncClient + Mock article_service |
| 集成 | 完整管线：generate → judge → store → GET article | Mock LLM，真实 DB |

### Mock LLM 核心模式

```python
# conftest.py 补充
@pytest.fixture
def mock_llm_response():
    """返回预设的 LLM JSON 响应"""
    return {
        "title": "The Impact of AI on Education",
        "segments": [
            {"segment_index": 0, "segment_type": "heading", "content": "..."},
            {"segment_index": 1, "segment_type": "paragraph", "content": "..."}
        ],
        "word_count": 350,
        "cefr_level": "B2"
    }

@pytest.fixture
def mock_content_generator(mocker, mock_llm_response):
    """Mock ContentGenerator Agent"""
    return mocker.patch(
        "app.agents.content_generator.ContentGenerator.generate",
        return_value=GenerationResult(**mock_llm_response)
    )

@pytest.fixture
def mock_content_judge(mocker):
    """Mock ContentJudge Agent"""
    return mocker.patch(
        "app.agents.content_judge.ContentJudge.judge",
        return_value=JudgeResult(score=0.85, passed=True, feedback="")
    )
```

## 陷阱

1. **LLM 返回无效 JSON**：始终 try/except JSON 解析并重试。使用 `response_format: { type: "json_object" }` 或结构化输出
2. **生成超时**：设置 LLM 调用超时（生成 30s、评判 15s），超时后作为失败处理
3. **不要事后分段**：让 LLM 直接生成分段结构（段落数组），事后用规则分段效果差
4. **保存生成元数据**：务必存储 prompt、模型名、token 用量到 `generation_metadata`，方便调试和成本追踪
5. **后台任务丢失**：服务器重启时 BackgroundTasks 会丢失，用 Redis 存储 task 状态（设 TTL），手动查 DB 恢复
6. **重试不无限循环**：最大重试 2 次（共 3 次尝试），仍不达标则标记为低质量存储，避免无限循环消耗 token
7. **LLM 限流 429**：OpenAI SDK 已内置重试，额外加 `asyncio.Semaphore(5)` 限制并发，3 次仍失败返回 503
8. **Admin 认证**：generate 端点必须校验 `X-Admin-Key` header，防止未授权触发大量 LLM 调用

## 验证标准

- `POST /admin/articles/generate` 返回 202 和有效 task_id
- 轮询 `generation-status` 从 processing → completed，article_id 有值
- 生成文章的 `quality_score` > 0（由评判 Agent 填充）
- `generation_metadata` 包含 model、token 用量等信息
- 生成失败（Mock LLM 返回错误）时状态变为 failed，error 有值
- 重试逻辑正确：Mock Judge 连续返回低分，验证最多重试 2 次
- `GET /api/v1/articles` 能看到新生成的已发布文章
- 所有测试通过：`pytest tests/ -v`
- 前端管理页能触发生成并显示进度/结果
