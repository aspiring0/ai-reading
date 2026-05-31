# Phase 3a: 用户认证与问卷

## 目标

实现用户注册/登录、JWT 认证、问卷定级（单页表单），更新阅读会话端点要求认证并填充 user_id。

## 前置条件

- Phase 2 完成：阅读核心功能可用，reading_sessions 表的 user_id 列已设为 nullable UUID
- 前端阅读页和辅助组件已实现
- LLM Agent 基类（base.py）可用

## 检查点与 Git 提交点

### Checkpoint 3a-1: 用户模型与安全工具

**涵盖任务**: 3a.1, 3a.2, 3a.3, 3a.4
**Git 分支**: `feature/P3a-1-user-model`

**提交时机**: User 模型、迁移、认证 schemas、security 工具全部完成后提交

**验证命令**:
1. `alembic upgrade head` → users 表创建成功
2. `pytest` → 密码哈希和 JWT token 相关测试通过
3. 手动验证: 在 Python shell 中执行 `from utils.security import hash_password, verify_password` → 无报错，可正常调用

---

### Checkpoint 3a-2: 认证 API

**涵盖任务**: 3a.5, 3a.6, 3a.7, 3a.8
**Git 分支**: `feature/P3a-2-auth-api`

**提交时机**: user_repo、auth_service、认证端点、dependencies 更新全部完成后提交

**验证命令**:
1. `pytest` → 认证测试通过（注册、登录、token 验证、重复邮箱）
2. `curl POST /api/v1/auth/register` → 返回 user + token，状态码 201
3. `curl POST /api/v1/auth/login` → 返回 token，状态码 200
4. `curl GET /api/v1/auth/me -H "Authorization: Bearer {token}"` → 返回用户信息
5. `curl GET /api/v1/auth/me`（无 token）→ 返回 401
6. `curl GET /api/v1/auth/me -H "Authorization: Bearer invalid_token"` → 返回 401

---

### Checkpoint 3a-3: 问卷引导

**涵盖任务**: 3a.9
**Git 分支**: `feature/P3a-3-onboarding`

**提交时机**: 问卷引导流程（简化单页）实现后提交

**验证命令**:
1. `curl POST /api/v1/auth/onboarding -H "Authorization: Bearer {token}" -d '{...}'` → 更新用户资料成功
2. 完成问卷后，`curl GET /api/v1/auth/me` → 显示 `onboarding_complete: true`

---

### Checkpoint 3a-4: 前端认证页面

**涵盖任务**: 3a.10, 3a.11, 3a.12, 3a.13
**Git 分支**: `feature/P3a-4-frontend-auth`

**提交时机**: 登录/注册页面、路由守卫、问卷页面、阅读会话认证集成全部完成后提交

**验证命令**:
1. `npm run dev` → 无报错
2. 访问 /register → 填写表单 → 提交 → 跳转到 /onboarding
3. 填写问卷 → 提交 → 跳转到首页
4. 登出 → 访问 /corpus → 跳转到 /login?redirect=/corpus
5. 登录 → 跳转回之前尝试访问的页面
6. 已登录状态访问 /login → 跳转到首页
7. 打开文章 → 阅读会话已关联 user_id（通过 API 确认）

---

## 任务清单

| # | 任务 | 复杂度 | 状态 |
|---|---|---|---|
| 3a.1 | 创建 models/user.py | 中 | ⬜ |
| 3a.2 | 创建迁移 | 低 | ⬜ |
| 3a.3 | 创建 schemas/auth.py | 中 | ⬜ |
| 3a.4 | 创建 utils/security.py | 中 | ⬜ |
| 3a.5 | 创建 repositories/user_repo.py | 中 | ⬜ |
| 3a.6 | 创建 services/auth_service.py | 高 | ⬜ |
| 3a.7 | 创建 api/v1/auth.py | 中 | ⬜ |
| 3a.8 | 更新 dependencies.py | 中 | ⬜ |
| 3a.9 | 创建问卷引导流程（简化单页） | 中 | ⬜ |
| 3a.10 | 编写认证测试 | 高 | ⬜ |
| 3a.11 | 前端：认证页面 | 中 | ⬜ |
| 3a.12 | 前端：问卷引导（简化单页） | 中 | ⬜ |
| 3a.13 | 更新阅读会话关联用户 | 中 | ⬜ |

### 任务详细说明

| # | 任务 | 详细说明 |
|---|---|---|
| 3a.1 | 创建 models/user.py | User、UserPreference 模型，见下方数据模型 |
| 3a.2 | 创建迁移 | `alembic revision --autogenerate -m "add users and user_preferences"` |
| 3a.3 | 创建 schemas/auth.py | RegisterRequest, LoginRequest, TokenResponse, UserResponse, OnboardingRequest |
| 3a.4 | 创建 utils/security.py | hash_password(), verify_password() 使用 passlib[bcrypt]；create_access_token(), decode_access_token() **使用 PyJWT（不用 python-jose，已不维护）**。依赖：PyJWT>=2.8 |
| 3a.5 | 创建 repositories/user_repo.py | get_by_email(), create_user(), update_user(), get_by_id() |
| 3a.6 | 创建 services/auth_service.py | register()、login()、get_current_user()。Token 有效期 7 天 |
| 3a.7 | 创建 api/v1/auth.py | POST /auth/register, /auth/login, GET /auth/me, PATCH /auth/me, POST /auth/onboarding |
| 3a.8 | 更新 dependencies.py | 添加 get_current_user() 依赖：提取 Bearer token、验证 JWT、返回用户对象。支持可选认证（get_optional_user）用于阅读端点过渡 |
| 3a.9 | 创建问卷引导流程（简化单页） | **单页表单 4 个字段**：英语水平（下拉）、兴趣标签（多选）、目标考试（下拉，可选）、每日阅读分钟数（数字输入）。不是多步向导 |
| 3a.10 | 编写认证测试 | 注册、登录、token 验证、过期 token、重复邮箱、密码验证 |
| 3a.11 | 前端：认证页面 | 登录、注册页，token 存 localStorage，Axios 拦截器加 Bearer |
| 3a.12 | 前端：问卷引导（简化单页） | **单页表单组件**，4 个字段，提交后跳转首页。不是多步向导 |
| 3a.13 | 更新阅读会话关联用户 | 阅读端点加认证（用 get_current_user 依赖），创建会话时存储 user_id。查词自动保存到语料库（用户可选，Phase 3b 实现 save_to_corpus 部分） |

## API 端点

```
POST /api/v1/auth/register
  认证：无
  请求体：{ "email", "password", "display_name" }
  响应 201: { "user": {...}, "access_token", "token_type": "bearer" }
  响应 409: {"detail": "Email already registered"}

POST /api/v1/auth/login
  认证：无
  请求体：{ "email", "password" }
  响应 200: { "access_token", "token_type", "user": {...} }
  响应 401: {"detail": "Invalid credentials"}

GET /api/v1/auth/me
  认证：Bearer token
  响应 200: { "id", "email", "display_name", "level", "onboarding_complete", ... }

PATCH /api/v1/auth/me
  认证：Bearer token
  请求体：{ "display_name", "native_language" }
  响应 200: 完整用户响应

POST /api/v1/auth/onboarding
  认证：Bearer token
  请求体：{
    "level": "intermediate",            // 英语水平
    "interests": ["technology", "science"], // 兴趣标签
    "target_exam": "IELTS",             // 目标考试（可选）
    "daily_goal_minutes": 15             // 每日阅读分钟数
  }
  响应 200: { "user": {...}, "recommended_articles": [...] }
```

## 数据模型变更

### users

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | UUID | PK, default uuid_generate_v4() | |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 登录标识 |
| password_hash | TEXT | NOT NULL | bcrypt 哈希 (work factor 12) |
| display_name | VARCHAR(100) | | 显示名 |
| level | VARCHAR(20) | NOT NULL, default 'intermediate' | beginner/intermediate/advanced |
| target_score | VARCHAR(20) | | 如 "IELTS 7.0" |
| native_language | VARCHAR(10) | default 'zh' | 翻译方向 |
| daily_goal_minutes | INTEGER | default 15 | 每日阅读目标 |
| onboarding_complete | BOOLEAN | default false | 是否完成问卷 |
| created_at | TIMESTAMPTZ | default now() | |
| updated_at | TIMESTAMPTZ | default now() | 触发器自动更新 |

索引：`UNIQUE INDEX idx_users_email ON (email)`

### user_preferences

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | UUID | PK | |
| user_id | UUID | FK users(id) CASCADE, UNIQUE | |
| interests | JSONB | default '[]' | 兴趣标签数组 |
| target_exam | VARCHAR(50) | | IELTS/TOEFL/GRE 等 |
| created_at | TIMESTAMPTZ | default now() | |
| updated_at | TIMESTAMPTZ | default now() | |

### reading_sessions 变更

- user_id 列已存在（Phase 2 创建时设为 nullable），现在通过认证填充

## 设计模式

1. **依赖注入（认证）**：get_current_user 作为 FastAPI 依赖注入到需要认证的端点
2. **可选认证**：get_optional_user 用于过渡期，未登录返回 None，已登录返回用户对象
3. **拦截器模式（前端）**：Axios 拦截器自动附加 Bearer token，401 自动跳转登录

## 测试要求

| 层 | 测试内容 | 方式 |
|---|---|---|
| 单元 | security.py：密码哈希、JWT 创建/验证 | pytest，测试正确密码验证通过、错误密码失败 |
| 单元 | security.py：token 过期、无效 token | 测试过期 token 抛异常 |
| Service | auth_service：注册（正常、重复邮箱） | Mock Repository，测试注册流程和冲突 |
| Service | auth_service：登录（正常、错误密码） | Mock Repository，测试登录流程 |
| API | 认证端点 | httpx.AsyncClient，测试注册、登录、获取个人信息、更新、问卷 |
| API | 认证保护 | 测试未认证访问受保护端点返回 401 |
| API | 重复注册 | 测试重复邮箱返回 409 |
| 前端 | 认证流程 | Vitest：登录表单提交、token 存储、路由跳转 |

## 陷阱

1. **密码存储**：始终用 bcrypt（work factor 12），绝不用 MD5/SHA256
2. **JWT 密钥管理**：必须在环境变量中，开发用 .env，生产用密钥管理器
3. **JWT 库选择**：使用 PyJWT（不用 python-jose，已超过 2 年无维护更新）。迁移成本极低（仅 security.py 一个文件）
4. **Token 有效期**：7 天，不要设太短导致频繁重新登录
5. **问卷不要做多步向导**：MVP 只需单页表单 4 个字段，不需要多步动画
6. **前端路由守卫**：统一在 router/index.ts 的 beforeEach 中处理认证逻辑，不在组件中单独判断
7. **onboarding 拦截**：onboarding_complete=false 的用户访问任何页面时跳转 /onboarding
8. **阅读端点过渡**：使用 get_optional_user 依赖，未登录用户仍可阅读（user_id=NULL），已登录用户自动填充 user_id

## 验证标准

- 注册新用户 -> 登录 -> 获取个人信息成功
- 无效密码登录返回 401
- 重复邮箱注册返回 409
- 过期 token 访问受保护端点返回 401
- 问卷提交后 onboarding_complete 设为 true
- 前端登录后 token 存入 localStorage，后续请求自动带 Bearer
- 阅读会话创建时，已登录用户的 user_id 正确填充
- 前端路由守卫生效：未登录访问 /corpus 跳转 /login
