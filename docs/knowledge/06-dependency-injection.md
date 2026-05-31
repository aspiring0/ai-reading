# FastAPI 依赖注入

## 什么是依赖注入

简单说：函数需要的"工具"不自己创建，而是由外部传入。

```python
# 不用依赖注入 — 函数自己创建数据库连接
async def list_articles():
    session = AsyncSessionLocal()       # 自己创建
    result = await session.execute(...)
    await session.close()               # 自己关闭
    return result

# 用依赖注入 — FastAPI 自动传入数据库连接
@router.get("/articles")
async def list_articles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(...)      # 直接用，不用关心创建和关闭
    return result
```

好处：
1. 代码简洁 — 不用写创建/关闭连接的样板代码
2. 自动管理生命周期 — commit/rollback 由 get_db 处理
3. 方便测试 — 测试时可以替换 get_db 为假的数据库

## Depends() 怎么工作

```python
from fastapi import Depends

async def list_articles(db: AsyncSession = Depends(get_db)):
    ...
```

FastAPI 看到 `Depends(get_db)` 时的处理流程：

```
1. 发现参数 db 有 Depends(get_db)
2. 调用 get_db() 函数
3. get_db 执行到 yield session，把 session 返回
4. 把 session 赋值给 db 参数
5. 执行 list_articles 函数
6. 函数执行完毕，继续 get_db 中 yield 后面的代码（commit/rollback）
```

## 嵌套依赖

依赖可以嵌套：一个依赖可以依赖另一个依赖。

```python
# get_current_user 依赖 get_db
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),  # 从请求头提取 token
) -> User:
    payload = jwt.decode(token)
    user = await db.get(User, payload["user_id"])
    return user

# API 端点依赖 get_current_user
@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    return user
```

FastAPI 自动解析依赖链，按正确顺序调用。

## 为什么 dependencies.py 和 database.py 都有 get_db

database.py 的 get_db 是"原始版本"，dependencies.py 的是"统一入口"。实际上现在两个一样。后面 dependencies.py 会成为唯一的入口，database.py 只负责引擎和会话工厂的创建。这样分层的好处是：database.py 改了引擎实现，不需要改 dependencies.py 的逻辑。

## Request 对象

```python
from fastapi import Request

def get_redis(request: Request) -> aioredis.Redis:
    return request.app.state.redis
```

`Request` 是 FastAPI 提供的特殊类型——不需要 `Depends()`，直接写在参数里就能用。它包含当前请求的所有信息：
- `request.app` — FastAPI 应用实例
- `request.state` — 当前请求的临时存储
- `request.headers` — 请求头
- `request.method` — HTTP 方法（GET/POST/...）

通过 `request.app.state.redis` 就能访问到 lifespan 里存的 Redis 连接。
