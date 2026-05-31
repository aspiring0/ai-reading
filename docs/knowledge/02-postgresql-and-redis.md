# PostgreSQL 和 Redis

## 为什么用两个

PostgreSQL 存**重要的永久数据**：用户账号、文章内容、学习记录。这些数据不能丢。

Redis 存**临时的缓存数据**：刚查过的单词释义、正在生成的文章状态。丢了也无所谓，重新算就行。

## 为什么不只用 PostgreSQL

PostgreSQL 每次查询都要从硬盘读数据。如果 100 个人同时查 "ephemeral" 这个词，就要查 100 次数据库、调 100 次 LLM。

用 Redis：第一次查完把结果存到 Redis（在内存里），后面 99 个人直接从 Redis 读。内存比硬盘快几百倍。

## 连接串解读

```
postgresql+asyncpg://aireading:aireading_dev@localhost:5432/ai_reading
  ↓        ↓        ↓          ↓            ↓       ↓      ↓
数据库类型  驱动名    用户名      密码          主机地址  端口   数据库名
```

`+asyncpg` 是关键。正常 Python 连 PostgreSQL 用 psycopg2（同步驱动），但我们的 FastAPI 是异步的，必须用 asyncpg（异步驱动）。同步驱动会在等数据库响应时卡住整个服务器。

## 连接池

`create_async_engine()` 创建的不只是一个连接，而是一个连接池。默认维护多个连接，请求来了从池里拿一个，用完还回去。比每次请求都新建连接快得多。
