# 技术蓝图评审意见

> 评审日期：2026-05-31
> 评审对象：`docs/2026-05-31-ai-reading-technical-blueprint.md`（977行）
> 评审结论：**规划质量高，需要调整粒度和范围后执行**

---

## 总体评价

蓝图覆盖了架构、数据模型、API、测试、陷阱、并发考虑等维度，是业余项目中少见的扎实方案。主要问题不在规划质量，而在**执行可行性**：

1. 单文件 977 行，无法在开发中快速定位当前任务
2. 部分 Phase 任务量过大，兼职节奏下容易半途而废
3. MVP 包含了一些可以后补的功能，增加了首版交付风险

---

## 问题一：Phase 粒度太粗 + 文件管理缺失

### 问题分析

| Phase | 任务数 | 高复杂度任务 | 文件行数（预估） | 问题 |
|---|---|---|---|---|
| 0 | 22 | 5 | ~400行 | "项目骨架"包含了前后端+CI+Docker，一个Phase做了5件事 |
| 1 | 19 | 4 | ~350行 | CRUD 和 LLM 管线是完全不同的技术挑战，不应耦合 |
| 2 | 19 | 5 | ~350行 | 粒度合理，但前端组件拆分可以更细 |
| 3 | 26 | 4 | ~400行 | 认证+语料库+FSRS+推荐是4个域，塞一个Phase |
| 4 | 18 | 3 | ~300行 | 部署+完善可以分开 |

单文件 977 行的问题：
- 开发时需要在长文件中反复跳转
- 后续每个 Phase 的变更记录、实际进度会混在一起
- 新增文档（API文档、部署手册等）无组织结构

### 解决方案

**1. docs 目录结构化管理**（见 `docs/README.md`）

```
docs/
├── README.md                    # 文档索引与文件管理规范
├── reviews/                     # 评审记录
├── phases/                      # 每个 Phase 独立文件
├── architecture/                # 跨阶段架构文档
├── decisions/                   # 技术决策记录(ADR)
└── 2026-05-31-...blueprint.md   # 原始蓝图归档
```

**2. Phase 拆分为 8 个子阶段**

```
原 Phase 0（22任务）→ 拆为：
  Phase 0a: 后端骨架（12任务，~1周）  → health端点 + Docker + DB + CI
  Phase 0b: 前端骨架（6任务，~1周）   → Vue初始化 + 布局 + API客户端 + 路由

原 Phase 1（19任务）→ 拆为：
  Phase 1a: 文章CRUD（8任务，~1.5周） → 模型+Repo+Service+API+前端列表/详情
  Phase 1b: LLM生成管线（8任务，~2周） → Agent基类+生成+评判+管线+管理页

原 Phase 2（19任务）→ 保持：
  Phase 2: 阅读核心（19任务，~3周）   → 四层辅助+会话追踪+前端阅读器

原 Phase 3（26任务）→ 拆为：
  Phase 3a: 用户认证（8任务，~1.5周） → 注册/登录/JWT/问卷/前端认证
  Phase 3b: 语料库+FSRS（10任务，~2周） → 语料CRUD+FSRS复习+简单推荐+前端

原 Phase 4（18任务）→ 保持：
  Phase 4: 理解反馈+MVP完善（18任务，~2周） → 测验+仪表盘+部署
```

**3. 每个 Phase 文件的结构模板**

```markdown
# Phase Xx: 名称

## 目标
## 前置条件
## 任务清单
| # | 任务 | 复杂度 | 状态 |
|---|---|---|---|
| Xx.1 | ... | 中 | ⬜ |
## API 端点
## 数据模型变更
## 设计模式
## 测试要求
## 陷阱
## 验证标准
```

**4. 拆分后文件清单**

| 文件 | 行数预估 | 内容来源 |
|---|---|---|
| `architecture/overview.md` | ~120行 | 蓝图第一章（总体架构+技术栈+目录结构） |
| `phases/phase-0a-backend-skeleton.md` | ~180行 | 蓝图 Phase 0 的后端任务 |
| `phases/phase-0b-frontend-skeleton.md` | ~100行 | 蓝图 Phase 0 的前端任务 |
| `phases/phase-1a-article-crud.md` | ~150行 | 蓝图 Phase 1 的 CRUD 部分 |
| `phases/phase-1b-llm-generation-pipeline.md` | ~200行 | 蓝图 Phase 1 的 LLM 部分 |
| `phases/phase-2-reading-core.md` | ~300行 | 蓝图 Phase 2 全部 |
| `phases/phase-3a-user-auth.md` | ~180行 | 蓝图 Phase 3 的认证部分 |
| `phases/phase-3b-corpus-and-srs.md` | ~200行 | 蓝图 Phase 3 的语料库部分 |
| `phases/phase-4-feedback-and-mvp.md` | ~250行 | 蓝图 Phase 4 全部 |

### 拆分的关键原则

- **先能看到页面，再接入 LLM**：Phase 1a 不依赖 LLM，可以手动插入测试数据跑通全链路，建立信心后再在 1b 接入 AI
- **认证先于业务**：Phase 3a 只做登录注册，不做语料库，避免一个 Phase 同时改 auth 中间件 + 业务逻辑
- **跨阶段通用规范提取**：错误处理、测试策略、环境管理等移到 `architecture/` 下，不重复写在每个 Phase

---

## 问题二：MVP 范围微调

### 需要砍掉的功能

| 功能 | 所在 Phase | 砍掉理由 | 后补时机 |
|---|---|---|---|
| 简答题题型 | Phase 4 | LLM评估简答题不稳定，调试成本高。MVP只做选择题+判断题 | Phase 5+ |
| 高级推荐算法 | Phase 3b | "排除已读+优先未知词汇"增加复杂度。MVP用标签匹配难度即可 | Phase 5+ |
| 语料库导出（CSV/JSON） | Phase 3b | 非核心路径，后补极快（1个任务） | Phase 5+ |
| user_daily_stats 预计算 | Phase 4 | 仪表盘实时查即可，用户量小无性能问题 | 生产优化阶段 |
| 熔断器模式 | Phase 4 | MVP阶段连续5次LLM失败=API key问题，不是生产故障 | Phase 5+ |

### 需要简化的功能

| 功能 | 现有设计 | 简化方案 | 理由 |
|---|---|---|---|
| 问卷引导 | 多步表单向导（学习目标+考试+兴趣+每日目标） | 单页表单4个字段：水平/兴趣标签/目标考试/每日分钟 | MVP不需要向导动画 |
| 管理端认证 | Admin API Key（X-Admin-Key） | 保持，但明确写在 .env 的 ADMIN_API_KEY | 已足够简单 |
| 文章生成后台任务 | BackgroundTasks + Redis task 状态 | 保持，但明确标注"重启丢失task状态，手动查DB恢复" | MVP可接受 |

### 调整后的 MVP 核心路径

```
注册 → 登录 → 选水平/兴趣 → 看推荐文章列表 →
阅读文章（四层辅助）→ 保存词条到语料库 →
做选择题/判断题 → 看仪表盘 → FSRS复习卡片
```

### 修订后的 Phase 时间线

```
Phase 0a: 后端骨架        1周
Phase 0b: 前端骨架        1周
Phase 1a: 文章CRUD        1.5周
Phase 1b: LLM生成管线     2周
Phase 2:  阅读核心        3周
Phase 3a: 用户认证        1.5周
Phase 3b: 语料库+FSRS     2周
Phase 4:  理解反馈+完善    2周
                          ────
                          总计 ~14周兼职
```

---

## 问题三：CLAUDE.md 补充与规范检查

### 规范符合度检查

CLAUDE.md 是 Claude Code 的项目约束文件，核心要求是**可操作、无歧义、不冗长**。对照标准：

| 维度 | 现状 | 评价 |
|---|---|---|
| 项目概述 | ✅ 有 | 清晰 |
| 技术栈 | ✅ 有 | 不可更改——好 |
| 架构原则 | ✅ 有 | 分层+禁止事项——好 |
| 代码规范 | ✅ 有 | Python + TS + 命名——好 |
| Git工作流 | ✅ 有 | 分支+提交规范——好 |
| 数据库规范 | ✅ 有 | 迁移+主键+时间——好 |
| 错误处理 | ✅ 有 | 统一格式+异常层级——好 |
| 测试要求 | ✅ 有 | 分层+mock策略——好 |
| 安全规范 | ✅ 有 | 密码+JWT+CORS——好 |
| **日志规范** | ❌ 缺失 | 无日志库、无级别策略 |
| **前端路由守卫** | ❌ 缺失 | 无认证拦截规则 |
| **API版本化** | ❌ 缺失 | 提了v1但无版本规则 |
| **前端错误处理** | ❌ 缺失 | Axios拦截器策略未规定 |
| **docs管理规范** | ❌ 缺失 | 文档如何组织未提及 |
| **环境变量规范** | ⚠️ 不足 | 只说"不硬编码"，缺命名规则 |
| **JWT库选型** | ⚠️ 需更新 | python-jose 已不活跃 |

### 需要补充的内容

#### 1. 日志规范

```markdown
## 日志规范

- 使用 structlog（结构化日志，JSON输出，方便生产环境日志收集）
- 级别策略：
  - DEBUG：开发环境详细调试（SQL查询、LLM请求/响应）
  - INFO：业务事件（用户注册、文章生成、阅读完成）
  - WARNING：降级事件（LLM重试、缓存未命中回源）
  - ERROR：需要关注的错误（LLM连续失败、数据库连接断开）
- 禁止在日志中输出：密码、token、完整 LLM prompt（只记录前100字符+token数）
- Agent 每次调用记录：model, prompt_hash, input_tokens, output_tokens, duration_ms, success
```

#### 2. 前端路由守卫规则

```markdown
## 前端路由守卫

- 未登录访问需认证页面（/corpus, /dashboard, /settings）→ 跳转 /login?redirect=原路径
- 已登录访问 /login, /register → 跳转首页
- onboarding_complete=false 的用户访问任何页面 → 跳转 /onboarding
- 路由守卫统一在 router/index.ts 的 beforeEach 中处理，不在组件中单独判断
```

#### 3. 前端错误处理规则

```markdown
## 前端错误处理

- Axios 响应拦截器统一处理：
  - 401 → 清除 token，跳转 /login
  - 403 → toast "无权限"
  - 404 → toast "资源不存在"
  - 422 → 提取 errors 数组，展示字段级错误
  - 500/503 → toast "服务暂时不可用，请稍后重试"
- 组件内不处理上述通用错误，只处理业务特有错误（如"词条已存在"）
- LLM 相关功能加载中必须显示骨架屏或 loading 状态，不能空白
```

#### 4. API 版本化规则

```markdown
## API 版本化

- 当前版本 v1，所有端点在 /api/v1/ 下
- 引入 v2 的条件：破坏性变更（删除字段、改字段类型、改语义）
- 新增字段、新增端点不算破坏性变更，在 v1 内演进
- v2 引入后 v1 至少保留 3 个月
- 版本路由文件：api/v1/router.py, api/v2/router.py
```

#### 5. 环境变量命名规范

```markdown
## 环境变量

- 命名：大写+下划线，分组前缀（DB_, REDIS_, LLM_, AUTH_, CORS_）
- 必需变量在 config.py 中无默认值（启动即报错）
- 可选变量提供合理默认值
- .env.example 必须列出所有变量及说明
- 敏感变量（SECRET_KEY, API_KEY）绝不提交到 git
```

#### 6. JWT 库更新

```markdown
将 python-jose 替换为 PyJWT：
- python-jose 已超过2年无维护更新
- PyJWT 活跃维护，API 更简洁
- 迁移成本极低（仅 security.py 一个文件）
- requirements.txt: PyJWT>=2.8
```

#### 7. docs 管理规范

```markdown
## 文档管理

- 文档根目录：docs/
- 结构规范见 docs/README.md
- 每个 Phase 的执行计划在 docs/phases/ 下独立文件
- 技术决策用 ADR 格式记录在 docs/decisions/
- 原始蓝图归档不动，拆分后的 Phase 文件是执行版
```

#### 8. reading_sessions 预留 user_id

```markdown
## 数据模型注意事项

- Phase 2 创建 reading_sessions 时，user_id 列设为 nullable UUID
  - Phase 2 无认证时 user_id=NULL
  - Phase 3a 加认证后填充 user_id
  - 避免 Phase 3 大改迁移
```

---

## 执行建议

1. **先更新 CLAUDE.md**：把上面 7 项补充内容加入
2. **拆分蓝图**：按 docs/README.md 的结构把原始蓝图拆到 phases/ 和 architecture/ 下
3. **原始蓝图归档**：重命名加 `_archived` 后缀，不再修改
4. **按 Phase 0a 开始执行**

是否确认执行？
