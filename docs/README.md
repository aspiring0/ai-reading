# AI 英语阅读产品 — 文档索引

> 文档根目录：`docs/`
> 所有文档使用中文，日期格式 `YYYY-MM-DD`

## 目录结构

```
docs/
├── README.md                                    # 本文件：文档索引与文件管理规范
├── reviews/                                     # 评审记录（蓝图评审、架构评审等）
│   └── 2026-05-31-blueprint-review.md           # 技术蓝图首次评审意见
├── phases/                                      # 分期开发计划（从蓝图拆分）
│   ├── phase-0a-backend-skeleton.md             # 后端骨架
│   ├── phase-0b-frontend-skeleton.md            # 前端骨架
│   ├── phase-1a-article-crud.md                 # 文章模型与CRUD
│   ├── phase-1b-llm-generation-pipeline.md      # LLM内容生成管线
│   ├── phase-2-reading-core.md                  # 阅读核心（四层辅助+会话追踪）
│   ├── phase-3a-user-auth.md                    # 用户认证与问卷
│   ├── phase-3b-corpus-and-srs.md               # 语料库与间隔复习
│   └── phase-4-feedback-and-mvp.md              # 理解反馈与MVP完善
├── architecture/                                # 架构设计文档
│   └── overview.md                              # 总体架构（从蓝图第一章提取）
├── decisions/                                   # 技术决策记录 (ADR)
│   └── template.md                              # ADR模板
└── 2026-05-31-ai-reading-technical-blueprint.md # 原始完整蓝图（归档参考）
```

## 文件管理规范

### 命名规则

| 类型 | 命名格式 | 示例 |
|---|---|---|
| 评审记录 | `reviews/YYYY-MM-DD-{主题}-review.md` | `2026-05-31-blueprint-review.md` |
| 分期计划 | `phases/phase-{编号}-{英文短名}.md` | `phase-1a-article-crud.md` |
| 架构文档 | `architecture/{英文短名}.md` | `overview.md` |
| 技术决策 | `decisions/YYYY-MM-DD-{主题}.md` | `2026-06-01-jwt-library.md` |

### 新增文档流程

1. 确定文档类型（评审/计划/架构/决策）
2. 按命名规则创建文件
3. 在本 README 的目录结构中登记
4. 如涉及技术决策，同步创建 ADR

### 文档拆分原则

- **单文件不超过 500 行**：超过时拆分为多个子文档
- **每个 Phase 独立一个文件**：包含该 Phase 的任务、API、数据模型、陷阱
- **跨阶段通用规范放 `architecture/`**：不重复写在每个 Phase 中
- **原始蓝图归档不动**：拆分后的文件是"执行版"，蓝图是"参考版"

### 文档与代码同步

- Phase 计划文件中的任务编号与 Git 分支对应：`feature/P0a-0.3-setup-database`
- 任务完成后在 Phase 文件中标记 ✅
- 每个 Phase 结束时更新本 README 的进度状态
