# 依赖注入（Depends）

## 一句话解释

函数需要的东西不自己创建，让 FastAPI 自动传入。

## 不用依赖注入

```python
@router.get("/articles")
async def list_articles():
    # 自己创建数据库连接
    session = AsyncSessionLocal()
    try:
        result = await session.execute(select(Article))
        return result.scalars().all()
    finally:
        await session.close()    # 别忘了关闭
```

每个函数都要写创建连接、关闭连接的代码。忘了一个 close 就出问题。

## 用依赖注入

```python
@router.get("/articles")
async def list_articles(db: AsyncSession = Depends(get_db)):
    # db 是 FastAPI 自动传入的，不用管创建和关闭
    result = await db.execute(select(Article))
    return result.scalars().all()
```

`Depends(get_db)` 告诉 FastAPI："调用 get_db 函数，把结果传给我"。

## 为什么叫 "依赖注入"

"依赖" = 函数依赖的东西（数据库连接）
"注入" = 自动传入（不需要函数自己创建）

函数声明自己需要什么，框架负责提供。

## Depends 怎么工作

```
1. FastAPI 看到 db: AsyncSession = Depends(get_db)
2. 调用 get_db() 函数
3. get_db 创建数据库会话，yield 出来
4. FastAPI 把这个会话传给 list_articles 的 db 参数
5. list_articles 执行完毕
6. FastAPI 继续 get_db 中 yield 后面的代码（commit 或 rollback）
```

## Request 对象

```python
from fastapi import Request

def get_redis(request: Request):
    return request.app.state.redis
```

`Request` 是特殊类型，不需要 `Depends()`。FastAPI 看到参数类型是 `Request` 就自动传入当前请求对象。通过它可以访问到 `app.state` 上存的东西。
