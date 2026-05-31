# Alembic 与数据库迁移

## 什么是数据库迁移

当你写了一个新的 ORM 模型（比如 Article），数据库里还没有对应的表。你需要告诉数据库"请创建一个叫 articles 的表"。数据库迁移就是**用代码管理数据库结构变化**的过程。

类比：数据库迁移就像 Git，但管理的是数据库结构而不是代码。

```
alembic upgrade head     ←→    git pull（应用所有变更）
alembic downgrade -1     ←→    git revert（撤销一次变更）
alembic revision         ←→    git commit（创建一个新变更）
```

## 为什么需要迁移工具

不用迁移工具的做法：手动在数据库里执行 `CREATE TABLE ...`。问题：

1. 你本地创建了表，同事的数据库没有 → 他的代码报错
2. 上线时忘了建表 → 生产环境崩溃
3. 表结构改了，忘了通知其他人 → 全组报错

用 Alembic：每次表结构变化生成一个 Python 文件，提交到 git。所有人 `alembic upgrade head` 就能同步数据库结构。

## 迁移文件长什么样

每个迁移文件有两个函数：

```python
def upgrade() -> None:
    # 升级：创建表
    op.create_table(
        'articles',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        ...
    )

def downgrade() -> None:
    # 降级：删除表（回滚用）
    op.drop_table('articles')
```

## 为什么我们的 env.py 是异步的

Alembic 默认用同步方式连接数据库（psycopg2）。但我们项目用的是 `postgresql+asyncpg://`，驱动是异步的。所以 env.py 需要改写成异步版本：

```python
# 核心改动：用 asyncio.run() 包裹异步函数
async def run_async_migrations() -> None:
    connectable = async_engine_from_config(...)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)  # run_sync 把同步迁移代码放到异步环境里执行

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())  # 启动异步事件循环
```

## 工作流程

```bash
# 1. 创建/修改 ORM 模型后，自动检测变化生成迁移文件
alembic revision --autogenerate -m "add articles table"

# 2. 查看生成的文件，确认 SQL 正确
# 文件在 backend/alembic/versions/xxx_add_articles_table.py

# 3. 应用迁移到数据库
alembic upgrade head

# 4. 查看当前迁移状态
alembic current

# 5. 回退一步
alembic downgrade -1
```

## alembic/env.py 中的 import 机制

```python
from app.database import Base

# 每添加新模型文件时，在这里 import 一次
# from app.models.article import Article  # noqa: F401
```

为什么需要 import？因为 Alembic 通过 `Base.metadata` 检测所有继承 Base 的模型。如果模型没有被 import，Python 不会执行它的代码，Base 就不知道这个模型的存在。`noqa: F401` 是告诉 ruff "这个 import 看似没用，但实际需要"。
