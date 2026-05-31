# PostgreSQL 与 Redis

## 为什么项目里同时用了两个数据库

| | PostgreSQL | Redis |
|---|---|---|
| 存储方式 | 硬盘（持久化） | 内存（速度快，重启可能丢） |
| 数据类型 | 表格（行和列） | 键值对（key → value） |
| 适合存什么 | 用户、文章、语料库 | 缓存、临时任务状态 |
| 类比 | 图书馆（永久收藏） | 书桌（正在用的资料） |

一个具体例子：用户查词"ephemeral"的释义。

1. 第一次查：调用 LLM API → 花费 2 秒 → 结果存到 Redis → 返回给用户
2. 第二次查：先看 Redis → 有缓存 → 0.001 秒返回

Redis 的 value 设了过期时间（TTL），比如 24 小时后自动删除。过期后再查就重新调 LLM。

## PostgreSQL 连接串

```
postgresql+asyncpg://aireading:aireading_dev@localhost:5432/ai_reading
    |          |          |          |         |       |
    协议        驱动       用户名     密码      主机    端口   数据库名
```

- `postgresql+asyncpg` — 用 asyncpg 驱动（不是 psycopg2），因为我们的 FastAPI 是异步的
- 为什么不用 psycopg2：psycopg2 是同步驱动，会阻塞整个服务器。asyncpg 是纯异步，不会阻塞

## 连接池是什么

```python
# database.py
engine = create_async_engine(settings.DATABASE_URL)
```

`engine` 不只是一个连接，它是一个**连接池**。默认维护 5 个数据库连接，复用它们：

```
请求1 → 从池中取连接 → 查询 → 归还连接到池
请求2 → 从池中取连接 → 查询 → 归还连接到池
```

如果没有连接池，每个请求都新建连接 → 三次握手 → 认证 → 查询 → 关闭，非常慢。

## Redis 连接方式

我们的代码在 main.py 的 lifespan 里创建 Redis 连接：

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动时：创建 Redis 连接
    app.state.redis = aioredis.from_url(settings.REDIS_URL)
    yield
    # 应用关闭时：断开连接
    await app.state.redis.aclose()
```

`redis://localhost:6380/0` 中的 `0` 是 Redis 的数据库编号。Redis 默认有 16 个数据库（0-15），用不同编号可以隔离不同应用的数据。

## 用 python 代码操作 Redis 的例子

```python
# 设置缓存（带过期时间）
await redis.set("word:ephemeral", '{"meaning": "短暂的"}', ex=86400)  # ex=秒数，86400=24小时

# 读取缓存
value = await redis.get("word:ephemeral")  # 返回 bytes 或 None

# 删除缓存
await redis.delete("word:ephemeral")

# 检查是否存活
await redis.ping()  # 返回 True
```
