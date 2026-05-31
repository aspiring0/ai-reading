# 配置管理（pydantic-settings）

## 为什么需要配置文件

数据库密码、API Key 这些敏感信息不能写在代码里（会提交到 git，所有人都能看到）。所以要放在 `.env` 文件里，这个文件不提交到 git。

## config.py 和 .env 的关系

```
.env 文件（你填的密码、密钥）
    ↓ pydantic-settings 自动读取
config.py（定义需要哪些配置项）
    ↓ 代码里 import settings
其他文件通过 settings.DATABASE_URL 使用
```

config.py 定义"需要什么"，.env 提供"具体值"。

## 优先级

```
环境变量 > .env 文件 > config.py 里的默认值
```

比如 `DATABASE_URL`：
- 如果系统环境变量设了 → 用环境变量的
- 如果没有，看 .env 文件里有没有 → 有就用 .env 的
- 都没有 → 用 config.py 里写的默认值

## model_config 是什么

```python
model_config = {"env_file": ".env"}
```

告诉 pydantic-settings："去 `.env` 文件里读配置"。`model_config` 是 pydantic v2 的固定写法（v1 用 `class Config`）。

## 为什么是 settings = Settings() 单例

`settings` 在模块被导入时创建一次。Python 保证同一个模块只导入一次，所以所有地方用的都是同一个 settings 对象。不需要每次都读 .env 文件。
