# Phase 4: 理解反馈与 MVP 完善

## 目标

生成理解题（选择题+判断题）、评估答案、学习仪表盘（实时查询）、生产部署。MVP 完成。

## 前置条件

- Phase 3b 完成：语料库、FSRS 复习、推荐功能可用
- 用户认证和阅读核心功能全部正常
- 前端语料库页面和复习页已实现

## 检查点与 Git 提交点

### Checkpoint 4-1: 理解题生成与回答

**涵盖任务**: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7
**Git 分支**: `feature/P4-1-quiz-system`

**提交时机**: feedback 模型、迁移、schemas、question_generator agent、feedback_service、feedback 端点、测验缓存全部完成后提交

**验证命令**:
1. `alembic upgrade head` → quiz_questions 和 quiz_responses 表创建成功
2. `pytest` → 测验生成和评分测试通过
3. `curl GET /api/v1/articles/{id}/quiz` → 返回 1-3 道题目（仅 multiple_choice + true_false）
4. `curl POST /api/v1/feedback/quiz/{id}/answer -d '{"answer":"B"}'` → 返回 is_correct + explanation
5. `curl GET /api/v1/reading/sessions/{id}/results` → 返回阅读统计 + 测验统计的合并数据

---

### Checkpoint 4-2: 学习仪表盘

**涵盖任务**: 4.8, 4.9
**Git 分支**: `feature/P4-2-dashboard`

**提交时机**: dashboard_service 和 dashboard 端点全部完成后提交

**验证命令**:
1. `curl GET /api/v1/dashboard?period=week` → 返回 reading_stats、corpus_stats、quiz_stats、daily_activity
2. 新用户 → 仪表盘显示零值/空数据（不崩溃）
3. 阅读文章并完成测验后 → 仪表盘显示真实数据

---

### Checkpoint 4-3: 前端测验与仪表盘

**涵盖任务**: 4.10, 4.11, 4.12, 4.13
**Git 分支**: `feature/P4-3-frontend-dashboard`

**提交时机**: 测验组件、仪表盘页面、响应式设计、加载/错误/空状态全部完成后提交

**验证命令**:
1. `npm run dev` → 无报错
2. 阅读文章 → 完成阅读 → 出现测验
3. 回答测验 → 显示正确/错误 + 解析
4. 访问 /dashboard → 看到统计卡片 + 活动图表
5. 调整为移动端宽度 → 布局自适应（响应式）
6. 无数据状态下测试 → 显示有意义的空状态提示，非空白页

---

### Checkpoint 4-4: MVP 部署与全链路验证

**涵盖任务**: 4.14, 4.15, 4.16, 4.17, 4.18
**Git 分支**: `feature/P4-4-deploy`

**提交时机**: 生产 Docker Compose、Nginx 配置、错误处理审计、E2E 测试、文档全部完成后提交

**验证命令**:
1. `docker-compose -f docker-compose.prod.yml up` → 所有服务正常启动
2. `curl https://your-domain.com/health` → 返回 ok
3. `curl https://your-domain.com/api/v1/articles` → 返回数据
4. 完整 E2E 用户旅程测试:
   - 注册 → 登录 → 问卷 → 查看推荐文章 →
   - 阅读文章并使用辅助 → 保存到语料库 →
   - 完成测验 → 查看仪表盘 → 复习语料库卡片 →
   - 导出语料库 → 所有步骤正常
5. 错误场景: 断开 LLM API → 优雅降级（显示错误信息，不崩溃）
6. API 文档 /docs → 可访问且完整

---

## 任务清单

| # | 任务 | 复杂度 | 状态 |
|---|---|---|---|
| 4.1 | 创建 models/feedback.py | 中 | ⬜ |
| 4.2 | 创建迁移 | 低 | ⬜ |
| 4.3 | 创建 schemas/feedback.py | 中 | ⬜ |
| 4.4 | 创建 agents/question_generator.py | 高 | ⬜ |
| 4.5 | 创建 services/feedback_service.py | 高 | ⬜ |
| 4.6 | 创建 api/v1/feedback.py | 中 | ⬜ |
| 4.7 | 缓存生成的测验 | 中 | ⬜ |
| 4.8 | 创建 dashboard_service.py | 中 | ⬜ |
| 4.9 | 创建 api/v1/dashboard.py | 低 | ⬜ |
| 4.10 | 编写测验测试 | 高 | ⬜ |
| 4.11 | 前端：测验组件 | 高 | ⬜ |
| 4.12 | 前端：仪表盘页面 | 中 | ⬜ |
| 4.13 | 前端：响应式和完善 | 中 | ⬜ |
| 4.14 | 全链路集成测试 | 高 | ⬜ |
| 4.15 | 生产部署配置 | 高 | ⬜ |
| 4.16 | 错误处理审计 | 中 | ⬜ |
| 4.17 | 性能测试 | 中 | ⬜ |
| 4.18 | 文档 | 中 | ⬜ |

### 任务详细说明

| # | 任务 | 详细说明 |
|---|---|---|
| 4.1 | 创建 models/feedback.py | QuizQuestion、QuizResponse 模型。**题型只有 multiple_choice 和 true_false，不含 short_answer** |
| 4.2 | 创建迁移 | `alembic revision --autogenerate -m "add quiz questions and responses"` |
| 4.3 | 创建 schemas/feedback.py | QuizQuestionResponse, QuizSubmitRequest/Response。question_type 只含 'multiple_choice' / 'true_false' |
| 4.4 | 创建 agents/question_generator.py | 生成 1-3 道理解题，**只生成选择题和判断题**（不含简答题）。返回结构化 JSON。出题 prompt 必须包含文章难度和用户水平 |
| 4.5 | 创建 services/feedback_service.py | generate_quiz()：调用 QuestionGenerator 生成题目并缓存。submit_answer()：选择题/判断题精确匹配判定对错，不需要 LLM 评估 |
| 4.6 | 创建 api/v1/feedback.py | 测验端点：获取测验、提交答案、获取阅读结果 |
| 4.7 | 缓存生成的测验 | 按文章 ID 缓存测验，key: `quiz:{article_id}`，TTL 1 小时。首次请求后生成，后续命中缓存 |
| 4.8 | 创建 dashboard_service.py | 聚合查询：已读文章数、总时长、语料量、复习正确率、连续天数。**直接实时查询数据库，不做预计算，不建 user_daily_stats 表** |
| 4.9 | 创建 api/v1/dashboard.py | 仪表盘端点，支持 period 参数（week/month/all） |
| 4.10 | 编写测验测试 | 题目生成（Mock LLM）、答案评估（选择题/判断题精确匹配）、分数计算 |
| 4.11 | 前端：测验组件 | 选择题单选按钮、判断题对错按钮、提交显示结果和解析。**不含简答题输入框** |
| 4.12 | 前端：仪表盘页面 | 统计卡片（文章数、时长、语料量、正确率）+ 简单柱状图（每日活动） |
| 4.13 | 前端：响应式和完善 | 移动端适配、加载状态（骨架屏）、错误状态、空状态 |
| 4.14 | 全链路集成测试 | 完整用户旅程：注册 -> 问卷 -> 推荐 -> 阅读 -> 辅助 -> 保存到语料库 -> 测验 -> 仪表盘 -> 复习 |
| 4.15 | 生产部署配置 | Docker Compose 生产配置、Nginx + SSL、部署脚本（含 alembic upgrade head）、数据库备份 |
| 4.16 | 错误处理审计 | 确保所有 API 返回正确错误格式，前端友好错误信息，LLM 失败优雅降级（重试 -> 降级响应 -> 503） |
| 4.17 | 性能测试 | 阅读端点负载测试、数据库查询优化、缓存命中率 |
| 4.18 | 文档 | API 文档（FastAPI 自动生成）、README 部署指南 |

## API 端点

```
GET /api/v1/articles/{article_id}/quiz
  认证：Bearer token
  响应 200:
    { "article_id", "questions": [
        { "id", "question_text", "question_type": "multiple_choice"|"true_false",
          "options", "difficulty" }
      ] }

POST /api/v1/feedback/quiz/{question_id}/answer
  认证：Bearer token
  请求体：{ "session_id", "answer", "time_taken_seconds" }
  响应 200:
    { "question_id", "is_correct", "user_answer", "correct_answer",
      "explanation" }

GET /api/v1/reading/sessions/{session_id}/results
  认证：Bearer token
  响应 200:
    { "session_id", "article_title",
      "reading_stats": { "duration_seconds", "words_per_minute", "words_looked_up" },
      "quiz_stats": { "total_questions", "correct_answers", "score_percentage" } }

GET /api/v1/dashboard
  认证：Bearer token
  查询参数：period(week|month|all)
  响应 200:
    { "reading_stats": { "articles_read", "total_reading_time_minutes",
        "average_reading_speed_wpm", "reading_streak_days" },
      "corpus_stats": { "total_entries", "reviews_completed", "review_accuracy", "due_for_review" },
      "quiz_stats": { "quizzes_taken", "average_score" },
      "daily_activity": [{ "date", "articles_read", "reading_minutes", "reviews_done" }],
      "level_progress": { "current_level", "estimated_cefr", "progress_to_next" } }
```

## 数据模型变更

### quiz_questions

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | UUID | PK | |
| article_id | UUID | FK articles(id) | |
| question_text | TEXT | NOT NULL | |
| question_type | VARCHAR(20) | NOT NULL | **'multiple_choice' / 'true_false'**（不含 short_answer） |
| options | JSONB | | 选择题选项 |
| correct_answer | TEXT | NOT NULL | |
| explanation | TEXT | | 解析 |
| difficulty | VARCHAR(20) | | |
| created_at | TIMESTAMPTZ | default now() | |

### quiz_responses

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | UUID | PK | |
| user_id | UUID | FK users(id) | |
| question_id | UUID | FK quiz_questions(id) | |
| session_id | UUID | FK reading_sessions(id) | |
| user_answer | TEXT | NOT NULL | |
| is_correct | BOOLEAN | | |
| time_taken_seconds | INTEGER | | |
| created_at | TIMESTAMPTZ | default now() | |

## 设计模式

1. **模板方法（出题）**：QuestionGeneratorAgent 固定流程（读文章 -> 出题 -> 验证），不同题型用策略实现
2. **Facade（仪表盘）**：DashboardService 聚合多个服务数据为单一响应，前端一次调用
3. **Cache-Aside（测验缓存）**：首次请求生成并缓存，后续直接返回

### MVP 简化说明

- **题型**：只有 multiple_choice 和 true_false，不含 short_answer。简答题 LLM 评估不稳定，调试成本高，留到 Phase 5+
- **仪表盘查询**：实时查数据库，不做 user_daily_stats 预计算。MVP 阶段用户量小，无性能问题
- **无熔断器**：不实现熔断器模式。MVP 阶段 LLM 连续失败通常是 API key 问题，不是生产故障。LLM 调用失败处理：重试 2 次 -> 返回 503

## 生产部署架构

```
Nginx（SSL终结 + 静态文件 + 反向代理）
  └── Docker Compose
      ├── FastAPI (uvicorn, 2 workers)
      ├── PostgreSQL 16 (持久卷)
      └── Redis 7 (持久化)
```

### 部署流程

```bash
# 1. 拉取代码
git pull origin main

# 2. 运行数据库迁移（必须先于应用重启）
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 3. 重启应用
docker compose -f docker-compose.prod.yml up -d --build

# 4. 验证
curl https://your-domain.com/health
```

### docker-compose.prod.yml 关键配置

```yaml
services:
  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
    environment:
      - ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    # Nginx 提供静态文件 + 反向代理到 backend

  postgres:
    image: postgres:16
    volumes:
      - pgdata:/var/lib/postgresql/data
    # 不暴露端口到外部

  redis:
    image: redis:7-alpine
    volumes:
      - redisdata:/data
    command: redis-server --appendonly yes

volumes:
  pgdata:
  redisdata:
```

## 测试要求

| 层 | 测试内容 | 方式 |
|---|---|---|
| Agent 单元 | QuestionGenerator 产出有效 JSON | Mock LLM，测试只生成 multiple_choice 和 true_false |
| Service | 测验生成和缓存 | Mock Agent 和 Redis，测试首次生成、缓存命中 |
| Service | 答案判定 | 选择题/判断题精确匹配，测试对错判定和分数计算 |
| Service | 仪表盘聚合 | Mock 多个 Repository，测试数据聚合逻辑 |
| API | 测验端点 | httpx.AsyncClient，测试获取测验、提交答案、阅读结果 |
| API | 仪表盘端点 | 测试不同 period 参数返回正确数据范围 |
| E2E | 完整用户旅程 | Playwright：注册 -> 问卷 -> 阅读 -> 测验 -> 仪表盘 |
| 性能 | 阅读端点负载 | k6 或 locust，测试辅助端点并发性能 |

## 陷阱

1. **测验难度不匹配**：出题 Agent 必须知道文章难度和用户水平，都写入 prompt
2. **只做选择题和判断题**：不实现简答题。答案判定用精确匹配，不需要 LLM 评估，简化实现
3. **仪表盘实时查询**：直接查数据库，不做预计算。确保关键查询有索引支持（reading_sessions 的 user_id+started_at 索引）
4. **空数据状态**：新用户看到空仪表盘，设计有意义的空状态提示（如"开始你的第一篇阅读"）
5. **部署忘迁移**：部署脚本必须先 alembic upgrade head 再重启应用
6. **Nginx 配置**：前端静态文件 + /api 反向代理到 backend，WebSocket 用于未来扩展
7. **SSL 证书**：使用 Let's Encrypt + certbot 自动续期
8. **数据库备份**：生产环境必须有定时 pg_dump 备份策略

## 验证标准

### 阶段验证

- 阅读文章后可生成测验（1-3 道选择题/判断题）
- 提交答案后显示对错和解析
- 仪表盘正确显示：阅读统计、语料统计、测验统计、每日活动
- 前端响应式：移动端和桌面端正常显示
- 所有错误场景返回正确的错误格式

### MVP 完成验证（完整用户旅程）

1. 注册新用户 -> 登录
2. 完成定级问卷（单页 4 字段）
3. 看到个性化推荐文章
4. 阅读文章，使用四层辅助（词义、短语、句子、段落）
5. 保存词条到语料库
6. 完成理解题（选择题/判断题），查看结果
7. 打开仪表盘，看到学习数据
8. 复习语料库中的卡片（FSRS）
9. 导出语料库为 CSV/JSON
10. 生产环境部署成功，`/health` 端点返回 OK
