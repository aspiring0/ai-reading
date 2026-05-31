# 前端基础概念

## Vue 是什么

Vue 是一个 **前端框架**，让你用 JavaScript 写网页界面。

没有 Vue 的写法（原生 HTML + JS）：
```html
<button onclick="loadArticles()">加载文章</button>
<div id="list"></div>

<script>
function loadArticles() {
  fetch('/api/v1/articles')
    .then(res => res.json())
    .then(data => {
      document.getElementById('list').innerHTML = data.items
        .map(a => '<div>' + a.title + '</div>')
        .join('')
    })
}
</script>
```

用 Vue 的写法：
```vue
<template>
  <button @click="loadArticles">加载文章</button>
  <div v-for="article in articles" :key="article.id">
    {{ article.title }}
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { getArticles } from '@/api/articles'

const articles = ref([])

async function loadArticles() {
  articles.value = await getArticles()
}
</script>
```

**Vue 的好处**：
- 数据变了，页面自动更新（不需要手动操作 DOM）
- 组件化：一个 `.vue` 文件 = 一个独立的页面片段，可以复用
- TypeScript 支持：类型检查，和后端一样安全

类比给 Python 开发者：Vue 之于前端，就像 FastAPI 之于后端。FastAPI 帮你处理 HTTP 请求/响应，Vue 帮你处理页面渲染/交互。

## Vite 是什么

Vite 是 Vue 的**开发服务器和打包工具**。

| 概念 | 后端对应物 | 作用 |
|---|---|---|
| Vite | uvicorn | 启动开发服务器，热更新 |
| npm run dev | uvicorn app.main:app --reload | 启动开发模式 |
| npm run build | — | 把源代码编译成浏览器能直接运行的文件 |
| dist/ 文件夹 | — | 编译产物（相当于 Java 的 .jar） |

开发时：`npm run dev` → Vite 启动在 5173 端口，代码改了页面自动刷新。
部署时：`npm run build` → 生成 dist/ 文件夹，放到 Nginx 上提供服务。

## Axios 是什么

Axios 是前端发 HTTP 请求的**库**。相当于 Python 的 httpx。

```typescript
// 前端用 Axios 调后端接口
const response = await axios.get('/api/v1/articles')
// 等价于 Python 里：
// response = await httpx.AsyncClient().get('/api/v1/articles')
```

我们的项目把它封装在 `src/api/index.ts` 里，加了拦截器（自动加 token、统一错误处理）。

## 前端目录结构

```
frontend/src/
├── main.ts           ← 入口（相当于 backend/app/main.py）
├── App.vue           ← 根组件（最外层布局）
├── router/index.ts   ← 路由配置（哪个 URL 显示哪个组件）
├── views/            ← 页面级组件（一个 .vue = 一个页面）
│   ├── HomeView.vue
│   └── ArticlesView.vue
├── components/       ← 可复用组件（按钮、卡片等）
├── api/              ← API 调用（相当于后端的 httpx 客户端）
│   ├── index.ts      ← Axios 实例
│   └── health.ts     ← 调 /health 的函数
├── stores/           ← 状态管理（Pinia，相当于全局变量）
└── assets/           ← 静态资源（CSS、图片）
```

## .vue 文件是什么

每个 `.vue` 文件由三部分组成：

```vue
<template>
  <!-- HTML 结构 — 页面长什么样 -->
</template>

<script setup lang="ts">
// JavaScript/TypeScript — 逻辑（获取数据、处理事件）
</script>

<style scoped>
/* CSS — 样式（只对当前组件生效，scoped 不会影响其他组件） */
</style>
```

类比：`.vue` 文件就像一个"自包含的页面部件"，有自己的界面、逻辑和样式。

## 前后端数据怎么流通

以"加载文章列表"为例：

```
1. 用户打开 /articles 页面
       ↓
2. Vue Router 显示 ArticlesView.vue 组件
       ↓
3. 组件调用 api/articles.ts 里的 getArticles()
       ↓
4. getArticles() 用 Axios 发 GET /api/v1/articles
       ↓
5. Vite 代理转发到后端 localhost:8000
       ↓
6. FastAPI api/v1/articles.py 接收请求
       ↓
7. 调用 article_service.get_published_articles()
       ↓
8. 调用 article_repo 查数据库
       ↓
9. 返回 JSON [{id, title, difficulty, ...}]
       ↓
10. Axios 收到响应，getArticles() 返回数据
       ↓
11. Vue 组件拿到数据，渲染成 HTML 显示给用户
```

用户在前端输入的参数（比如搜索关键词、选择的难度）在步骤 4 作为查询参数传递：
```typescript
// 前端
axios.get('/api/v1/articles', { params: { difficulty: 'hard', page: 1 } })
// 相当于 GET /api/v1/articles?difficulty=hard&page=1

# 后端
@router.get("/articles")
async def list_articles(difficulty: str = None, page: int = 1, db = Depends(get_db)):
    # 拿到前端传来的 difficulty 和 page 参数
    ...
```
