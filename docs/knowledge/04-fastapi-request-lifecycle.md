# FastAPI 请求生命周期

## 一个请求从到达到响应的完整过程

以 `curl http://localhost:8000/health` 为例：

```
1. 浏览器/curl 发出请求
2. Uvicorn（ASGI 服务器）接收请求
3. FastAPI 中间件处理（CORS 检查等）
4. 路由匹配 → 找到 health() 函数
5. 执行依赖注入（如果有的话）
6. 执行 health() 函数体
7. 返回响应
8. 中间件后处理
9. Uvicorn 把响应发回给浏览器/curl
```

## lifespan — 应用启动和关闭

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # ← 这里写启动逻辑（yield 之前）
    app.state.redis = aioredis.from_url(settings.REDIS_URL)

    yield  # ← 应用运行中，等待关闭信号

    # ← 这里写关闭逻辑（yield 之后）
    await app.state.redis.aclose()
```

`@asynccontextmanager` 是 Python 的上下文管理器装饰器。`yield` 把函数分成两半：前半段在启动时执行，后半段在关闭时执行。

### 为什么不直接在模块顶部创建 Redis 连接

```python
# 错误做法
redis = aioredis.from_url(...)  # 模块导入时就连接了
```

问题：如果 Redis 还没启动（比如你忘了 `docker compose up`），导入这个模块就会报错，连 `pytest` 都跑不了。放在 lifespan 里，只有真正启动服务时才连接。

## CORS 中间件

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    ...
)
```

为什么需要 CORS：浏览器有同源策略。前端在 `localhost:5173`，后端在 `localhost:8000`，浏览器认为这是"跨域请求"，默认会阻止。CORS 中间件告诉浏览器"这些域名是允许的"。

注意：CORS 是**浏览器限制**，curl/Postman 不受影响。所以你在终端 curl 正常但浏览器里可能报错。

## app.state — 应用全局状态

```python
app.state.redis = aioredis.from_url(...)
```

`app.state` 是 FastAPI 提供的一个对象，可以在上面挂任意属性。用来存储整个应用共享的资源（如 Redis 连接、数据库连接池等）。

### 为什么在 dependencies.py 里能访问到

```python
def get_redis(request: Request) -> aioredis.Redis:
    return request.app.state.redis
```

- `request: Request` — FastAPI 自动把当前请求对象传进来
- `request.app` — 通过请求对象获取 FastAPI 应用实例
- `.state.redis` — 从应用实例上取到 lifespan 里存的 Redis 连接

这就是为什么能从 request 追溯到 app 再到 redis。FastAPI 的 Request 对象持有 app 的引用。

## 路由挂载

```python
app.include_router(v1_router, prefix="/api/v1")
```

这行代码把 `v1_router` 里定义的所有端点加到 `/api/v1` 前缀下。比如以后在 `articles.py` 里定义 `@router.get("/articles")`，完整路径就是 `/api/v1/articles`。

这样做的好处：以后要加 v2 版本的 API，只需要加一个新的 router 和 prefix `/api/v2`，v1 不受影响。
