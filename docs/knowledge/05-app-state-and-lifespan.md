# app.state 和 lifespan

## app.state 是什么

`app.state` 是 FastAPI 提供的一个"公共储物柜"。你可以在上面存任何东西，整个应用都能访问。

```python
# 启动时：把 Redis 连接放进储物柜
app.state.redis = aioredis.from_url(...)

# 任何地方：从储物柜里取出 Redis 连接
redis = request.app.state.redis
```

**为什么叫 state**：state 就是"状态"。app.state 存的是整个应用级别的状态（比如 Redis 连接、数据库连接池）。这些不是某个请求私有的，而是所有请求共享的。

**为什么不直接用全局变量**：其实可以。但 app.state 是 FastAPI 推荐的方式，好处是：
1. 测试时可以替换 app.state.redis 为假的 Redis
2. 明确表示"这是应用级别的共享资源"

## lifespan 是什么

lifespan 管理应用的**启动和关闭**。

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ← 应用启动时执行这里
    app.state.redis = aioredis.from_url(...)  # 连接 Redis

    yield  # ← 分界线，应用正常运行中

    # ← 应用关闭时执行这里
    await app.state.redis.aclose()  # 断开 Redis
```

**为什么需要 lifespan**：
- Redis 连接不能在每次请求时创建（太慢），要在应用启动时创建一次
- 应用关闭时要断开连接，否则占着资源不放

**yield 是什么**：Python 语法，意思是"暂停这里，先去干别的事"。这里 yield 之前是启动代码，yield 之后是关闭代码。

## request.app.state.redis 怎么串起来的

```
1. main.py 启动时：
   app.state.redis = aioredis.from_url(...)
   ↑ 把 Redis 连接存在 app.state 上

2. 请求进来，FastAPI 自动把请求信息打包成 Request 对象

3. dependencies.py 里：
   request.app          → 通过请求对象找到 FastAPI 应用实例
   request.app.state    → 找到应用的公共储物柜
   request.app.state.redis → 从储物柜里取出 Redis 连接

4. 用这个连接操作 Redis：
   await request.app.state.redis.ping()
```

整条链路：`request → app → state → redis`
