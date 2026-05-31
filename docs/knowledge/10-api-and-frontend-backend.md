# API 设计与前后端通信

## 为什么接口要有 /api/v1/ 前缀

```
GET /health                    ← 运维用的健康检查，不在版本控制内
GET /api/v1/articles           ← 业务接口，版本 v1
POST /api/v1/auth/login        ← 业务接口，版本 v1
```

**为什么加版本号**：
- 以后接口可能要大改（比如返回数据格式完全不同）
- 加了 v1，旧版客户端继续用 v1，新客户端用 v2
- 不加版本号，改了接口所有客户端立刻报错

**什么时候加 v2**：只有"破坏性变更"才加（删字段、改字段类型）。新增字段、新增接口不算破坏性变更，在 v1 里加就行。

## 为什么需要 /health 端点

```python
@app.get("/health")
async def health():
    # 检查数据库能不能连
    # 检查 Redis 能不能连
    return {"status": "ok", "database": "connected", "redis": "connected"}
```

这个接口不是给用户用的，是给运维和 Docker 用的：
- Docker 用它判断容器是否健康，不健康就重启
- 部署后用它验证服务是否正常启动
- 监控系统定时调用，挂了就发告警

## 前端怎么调用后端接口

```
浏览器输入 URL
    ↓
Vue 组件调用 api/articles.ts 里的函数
    ↓
apiClient（Axios 实例）发 HTTP 请求
    ↓
Vite 开发代理 → 转发到后端 localhost:8000
    ↓
FastAPI 处理请求，返回 JSON
    ↓
Vue 组件拿到数据，渲染页面
```

## Vite 代理是什么

开发时前端在 5173 端口，后端在 8000 端口。前端代码写 `fetch('/api/v1/articles')`，浏览器实际请求的是 `localhost:5173/api/v1/articles`。

Vite 代理的作用：检测到 `/api` 开头的请求，自动转发到 `localhost:8000`。

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',  // 转发到后端
      changeOrigin: true,
    },
  },
}
```

**为什么需要代理**：直接请求 `localhost:8000` 会触发浏览器的 CORS（跨域）限制。代理让浏览器以为在请求同一个域，绕过了 CORS。

**生产环境不需要代理**：生产环境用 Nginx 反向代理，直接把 `/api` 请求转发给后端。

## Axios 拦截器做了什么

每次请求和响应都会经过拦截器，自动处理通用逻辑：

**请求拦截器**（发请求前）：
```typescript
// 自动在请求头加上 JWT token
const token = localStorage.getItem('access_token')
config.headers.Authorization = `Bearer ${token}`
```
好处：不用每个接口手动加 token，写一次全局生效。

**响应拦截器**（收到响应后）：
```typescript
// 统一错误处理
case 401:  // token 过期 → 清除 token，跳转登录页
case 403:  // 无权限 → 提示
case 404:  // 不存在 → 提示
case 500:  // 服务器错误 → 提示"服务暂时不可用"
```
好处：不用每个接口写 try/catch，写一次全局生效。

## 完整的接口规划（全部）

以下是我们这个项目最终会有的所有接口：

### 公开接口（不需要登录）
| 方法 | 路径 | 用途 | Phase |
|---|---|---|---|
| GET | /health | 健康检查 | 0 ✅ |
| GET | /api/v1/articles | 文章列表 | 1 |
| GET | /api/v1/articles/{id} | 文章详情 | 1 |

### 管理接口（需要 Admin Key）
| 方法 | 路径 | 用途 | Phase |
|---|---|---|---|
| POST | /api/v1/admin/articles/generate | 生成文章 | 1 |
| GET | /api/v1/admin/articles | 文章列表（含草稿） | 1 |
| PATCH | /api/v1/admin/articles/{id} | 更新文章 | 1 |
| DELETE | /api/v1/admin/articles/{id} | 删除文章 | 1 |

### 阅读接口（Phase 2）
| 方法 | 路径 | 用途 |
|---|---|---|
| POST | /api/v1/reading/sessions | 开始阅读 |
| PATCH | /api/v1/reading/sessions/{id} | 更新进度 |
| POST | /api/v1/reading/sessions/{id}/complete | 完成阅读 |
| POST | /api/v1/reading/assist | 获取辅助（查词等） |

### 用户接口（Phase 3）
| 方法 | 路径 | 用途 |
|---|---|---|
| POST | /api/v1/auth/register | 注册 |
| POST | /api/v1/auth/login | 登录 |
| GET | /api/v1/auth/me | 获取当前用户 |

### 语料库接口（Phase 3）
| 方法 | 路径 | 用途 |
|---|---|---|
| GET | /api/v1/corpus | 语料列表 |
| POST | /api/v1/corpus | 添加词条 |
| GET | /api/v1/corpus/reviews/due | 待复习词条 |
| POST | /api/v1/corpus/{id}/review | 提交复习结果 |

### 理解反馈接口（Phase 4）
| 方法 | 路径 | 用途 |
|---|---|---|
| GET | /api/v1/articles/{id}/quiz | 获取测验 |
| POST | /api/v1/feedback/quiz/{id}/answer | 提交答案 |
| GET | /api/v1/dashboard | 学习仪表盘 |

**为什么用不同的 HTTP 方法**：
- GET = 获取数据（不修改任何东西）
- POST = 创建新东西
- PATCH = 修改部分内容
- DELETE = 删除
这是 RESTful API 的约定，所有后端框架都遵循。

## 前端路由

```
/              → HomeView      首页（Phase 1 变成文章推荐列表）
/articles      → ArticlesView  文章列表（Phase 1 实现）
/corpus        → CorpusView    语料库（Phase 3 实现）
/about         → AboutView     关于页面
/login         → 登录页（Phase 3）
/register      → 注册页（Phase 3）
/dashboard     → 仪表盘（Phase 4）
```

**为什么用前端路由而不是多页面**：
传统网站每个 URL 对应一个 HTML 文件。Vue 是单页应用（SPA）——只有一个 HTML 文件，用 JavaScript 切换显示的内容。好处：
1. 切换页面不刷新，体验流畅
2. 前后端完全分离，后端只提供 API
3. 但需要在 Nginx 配置中把所有路由都指向 index.html
