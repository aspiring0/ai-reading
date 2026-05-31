# Phase 0b: 前端骨架

## 目标

搭建可运行的前端项目骨架，包含 Vue 3 + TypeScript + Pinia + Vue Router + TailwindCSS，创建基础布局、路由和 API 客户端骨架。完成后可通过 `docker-compose up` 全栈启动并验证前后端连通性。

## 前置条件

- Phase 0a（后端骨架）已完成，`/health` 端点可访问

## 当前进度

**已完成**: Checkpoint 0b-3 ✅（Phase 0b 全部完成）
**下一步**: Phase 1a — 内容管线后端
**Git 分支**: `feature/P0b-3-tooling-and-integration`

> 每个 checkpoint 完成后更新此节。新会话读此文件即可知道从哪继续。

## 检查点

### Checkpoint 0b-1: 前端项目初始化
**任务**: 0.14, 0.15
**Git 分支**: `feature/P0b-1-init-frontend`
**Git commit**: `chore(ui): init Vue 3 project with TailwindCSS`

验证步骤：
1. `cd frontend && npm install` — 安装无报错
2. `npm run dev` — Vite 启动，显示 localhost:5173
3. 浏览器打开 `http://localhost:5173` — 能看到默认页面
4. 确认 TailwindCSS 生效：页面有默认样式

### Checkpoint 0b-2: 布局 + API 客户端 + 路由
**任务**: 0.16, 0.17
**Git 分支**: `feature/P0b-2-layout-and-routing`
**Git commit**: `feat(ui): add basic layout, routing, and API client`

验证步骤：
1. `npm run dev` — 启动无报错
2. 浏览器打开 `http://localhost:5173` — 看到 AppHeader 和首页占位内容
3. 点击导航链接 — 路由跳转正常，无 404
4. 打开浏览器 DevTools Console — 无报错
5. 打开 Network 面板 — API 客户端初始化无报错（还没调 API，但不报错即可）

### Checkpoint 0b-3: 规范工具 + Docker + 全栈验证
**任务**: 0.19f, 0.21f, 0.22
**Git 分支**: `feature/P0b-3-tooling-and-integration`
**Git commit**: `chore(ui): add linting, Dockerfile, and full-stack verification`

验证步骤：
1. `npm run lint` — eslint 通过
2. `docker build -t ai-reading-frontend ./frontend` — Dockerfile 构建成功
3. `docker-compose up` — 全栈启动（backend + frontend + postgres + redis）
4. 浏览器打开 `http://localhost:5173` — 前端页面正常
5. `curl http://localhost:8000/health` — 后端健康检查正常
6. 前端页面 F12 Console — 无连接后端失败的错误

## 任务清单

| # | 任务 | 复杂度 | 状态 |
|---|---|---|---|
| 0.14 | 初始化前端：`npm create vue@latest`，选 TypeScript + Pinia + Vue Router | 低 | ✅ |
| 0.15 | 安装 TailwindCSS：`npm install -D tailwindcss @tailwindcss/vite`，配置 | 低 | ✅ |
| 0.16 | 创建前端 API 客户端骨架：Axios 实例，带 auth token 拦截器和错误处理 | 中 | ✅ |
| 0.17 | 创建基础布局和路由：AppHeader、HomeView（占位）、3 个占位路由 | 中 | ✅ |
| 0.19f | 配置前端代码规范工具：eslint + prettier | 低 | ✅ |
| 0.21f | 创建前端 Dockerfile：多阶段构建 | 中 | ✅ |
| 0.22 | 全栈启动验证：`docker-compose up` 端到端冒烟测试 | 低 | ✅ |

## API 端点

本阶段前端不新增 API 端点。前端通过 API 客户端骨架连接 Phase 0a 已完成的 `GET /health` 端点进行连通性验证。

## 数据模型变更

无。

## 设计模式

- **Axios 拦截器**：统一处理 auth token 注入和错误响应（401 跳转登录、403/404/500 toast 提示）
- **Pinia Store 骨架**：为后续状态管理预留结构
- **Vue Router 占位路由**：为后续页面预留路由结构

## 测试要求

- 前端 `npm run build` 构建无报错
- 前端 `npm run lint` 通过 eslint 检查
- 全栈启动后，前端页面可正常加载，能通过 API 客户端访问后端 `/health` 端点

## 陷阱

1. **Vite 代理配置**：开发时前端 5173 访问后端 8000 需要配置 Vite proxy，否则跨域
2. **TailwindCSS v4 配置变化**：v4 使用 `@tailwindcss/vite` 插件方式，与 v3 的 `tailwind.config.js` 不同
3. **TypeScript 严格模式**：初始化时启用严格模式，避免后期大量类型修补
4. **Node 版本**：使用 Node 20 LTS，通过 `.nvmrc` 指定版本

## 验证标准

- `docker-compose up` 全栈启动无报错
- 前端页面 `localhost:5173` 可访问，显示基础布局
- 前端 API 客户端可成功调用后端 `localhost:8000/health`，返回 200
- `npm run build` 构建成功
- `npm run lint` 通过 eslint 检查
