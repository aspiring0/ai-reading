# 数据库迁移（Alembic）

## 什么是数据库迁移

你写了一个 Python 类叫 `Article`，定义了 title、content 这些字段。但数据库里还没有这张表。你需要告诉数据库"创建一张叫 articles 的表，有这些列"。

数据库迁移 = **用代码记录数据库结构的变化**，像 Git 管理代码一样管理数据库结构。

## 为什么不直接手动建表

你可以在数据库里手动执行 `CREATE TABLE articles (...)`。问题：

1. 你的同事拉了代码，他的数据库里没有这张表 → 报错
2. 你加了一个新字段 `difficulty`，忘了告诉同事 → 他的代码报错
3. 上线时忘了在生产数据库加字段 → 线上崩溃

用 Alembic：每次改动生成一个 Python 文件（迁移文件），提交到 git。其他人拉代码后运行 `alembic upgrade head`，数据库自动同步。

## 迁移文件长什么样

每次表结构变化，Alembic 生成一个文件：

```python
def upgrade():
    # 升级：创建表
    op.create_table('articles',
        sa.Column('id', sa.UUID()),
        sa.Column('title', sa.String(500)),
    )

def downgrade():
    # 降级：撤销，删掉表
    op.drop_table('articles')
```

## 为什么要"异步迁移"

Alembic 默认用同步方式连数据库。但我们项目的连接串是 `postgresql+asyncpg://`（异步驱动）。如果 env.py 也是同步的，驱动对不上。所以 env.py 改成了异步版，用 `asyncio.run()` 包裹迁移操作。

## 日常使用

```bash
# 1. 改了 ORM 模型后，自动生成迁移文件
alembic revision --autogenerate -m "add articles table"

# 2. 应用迁移（让数据库变成最新结构）
alembic upgrade head

# 3. 查看当前状态
alembic current

# 4. 回退一步
alembic downgrade -1
```
