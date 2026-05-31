# pydantic-settings 与环境变量管理

## 为什么不用 os.environ 直接读

```python
# 直接读 — 没有类型转换，没有默认值，拼写错误不报错
db_url = os.environ.get("DATABASE_URL")  # 忘了设置就是 None，运行时才报错

# pydantic-settings — 启动时就检查，类型安全
class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://..."  # 有默认值
    PORT: int = 8000                                  # 自动转成 int

settings = Settings()  # 启动时立即校验所有字段
```

## 值的优先级

```
环境变量（最高优先级） > .env 文件 > 代码中的默认值（最低优先级）
```

例子：
```python
class Settings(BaseSettings):
    PORT: int = 8000  # 默认值
```

| 情况 | 结果 |
|---|---|
| 环境变量 PORT=9000 | 9000 |
| .env 文件有 PORT=9000，环境变量没有 | 9000 |
| 都没有 | 8000 |
| 环境变量 PORT=9000，.env 有 PORT=7000 | 9000（环境变量赢） |

## model_config 是什么

```python
class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
```

这是 pydantic v2 的写法（v1 用 `class Config`）。`model_config` 告诉 pydantic-settings：
- 去哪找 `.env` 文件（相对于工作目录，即 `backend/`）
- 文件编码是 utf-8

## @property 方法

```python
@property
def cors_origins_list(self) -> list[str]:
    return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
```

CORS_ORIGINS 在 .env 里是逗号分隔的字符串 `"http://localhost:5173,http://localhost:3000"`，但 FastAPI 中间件需要列表。`@property` 让你像访问属性一样调用方法：

```python
settings.CORS_ORIGINS        # → "http://localhost:5173,http://localhost:3000"（字符串）
settings.cors_origins_list   # → ["http://localhost:5173", "http://localhost:3000"]（列表）
```

## 单例模式

```python
settings = Settings()  # 模块级别，只创建一次
```

这个 `settings` 对象在 `app.config` 模块被导入时创建。Python 的模块导入机制保证同一个模块只执行一次，所以所有地方 `from app.config import settings` 得到的是同一个对象。

为什么不用 `Settings()` 每次都创建新实例？因为要读 .env 文件、校验字段，重复执行浪费性能。
