# Python 异步编程模式

## 同步 vs 异步

**同步**：一行一行执行，遇到慢操作（网络请求、数据库查询）就等着。

```python
# 同步 — 总耗时 = 2 + 3 = 5 秒
result1 = requests.get("https://api.example.com/1")  # 等 2 秒
result2 = requests.get("https://api.example.com/2")  # 等 3 秒
```

**异步**：遇到慢操作就先去做别的事，等结果回来了再继续。

```python
# 异步 — 总耗时 = max(2, 3) = 3 秒（同时发出两个请求）
result1, result2 = await asyncio.gather(
    httpx.get("https://api.example.com/1"),  # 2 秒
    httpx.get("https://api.example.com/2"),  # 3 秒
)
```

对于 Web 服务器：同步意味着一个请求在等数据库时，其他请求都在排队。异步意味着等待期间可以处理其他请求。100 个用户同时访问，异步服务器不需要 100 个线程。

## async/await 基本规则

```python
# 1. 用 async def 定义异步函数
async def fetch_data():
    # 2. 用 await 等待异步操作（不会阻塞整个程序）
    result = await db.execute("SELECT 1")
    return result

# 3. 调用异步函数必须用 await
data = await fetch_data()    # 正确
data = fetch_data()          # 错误 — 得到的是一个 coroutine 对象，不是结果
```

## 项目中的异步模式

### 数据库会话（get_db）

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session         # ← 把 session 交给路由函数使用
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

`yield` 让这个函数变成一个生成器。FastAPI 的依赖注入系统知道怎么处理它：
1. 请求进来 → 执行到 `yield`，把 session 给路由函数
2. 路由函数执行完毕 → 继续执行 `yield` 后面的 `commit()`
3. 出错 → 执行 `rollback()`

这就是为什么 get_db 能自动管理事务：请求成功就提交，失败就回滚。

### Redis 操作

```python
# 同步 Redis（不能用，会阻塞）
r = redis.Redis()
r.ping()

# 异步 Redis（我们用的）
r = aioredis.from_url(...)
await r.ping()
```

区别就是加了 `await`。异步 Redis 不会在等网络响应时阻塞整个服务器。

### LLM 调用（后面会写）

```python
async def generate_article(topic: str) -> Article:
    # 调用 LLM API 可能要 10-30 秒，异步等待期间可以处理其他请求
    response = await openai_client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "user", "content": f"写一篇关于{topic}的英语文章"}],
    )
    return parse_response(response)
```

## 什么时候用 async，什么时候不用

| 场景 | 用 async | 用 sync |
|---|---|---|
| 数据库操作 | asyncpg, SQLAlchemy async | - |
| HTTP 请求 | httpx.AsyncClient | requests |
| 文件读写（小文件） | - | open() 就行 |
| CPU 密集计算 | - | 不用 async，用多进程 |
| Redis | redis.asyncio | - |

**经验法则**：涉及网络/等待 I/O 的用 async，纯 CPU 计算的不用。
