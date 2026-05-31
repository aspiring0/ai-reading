"""
应用配置模块

使用 pydantic-settings 从环境变量和 .env 文件中加载配置。
优先级：环境变量 > .env 文件 > 代码中的默认值

使用方式：
    from app.config import settings
    print(settings.DATABASE_URL)
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """全局配置类，所有配置项集中管理。

    每个 Field 对应一个环境变量，类型注解决定了值的类型转换。
    例如 DATABASE_URL 是 str，如果环境变量不存在则使用默认值。
    """

    # Application
    ENV: str = "development"  # development / production，控制 SQL echo 日志等行为
    APP_VERSION: str = "0.1.0"

    # Database — 必须用 postgresql+asyncpg:// 驱动（不是 psycopg2）
    # Docker 环境中 host 用服务名 "postgres"，本地开发用 "localhost"
    DATABASE_URL: str = "postgresql+asyncpg://aireading:aireading_dev@localhost:5432/ai_reading"

    # Redis — 用于缓存和后台任务队列
    # 格式：redis://host:port/db_number
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security — JWT 签名密钥，生产环境必须更换为随机字符串
    SECRET_KEY: str = "change-me-to-a-random-secret"

    # LLM — OpenAI 兼容 API 配置
    # OPENAI_BASE_URL 可指向任何兼容接口（智谱、DeepSeek、Ollama、Azure 等）
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o"  # 智谱用 glm-5，DeepSeek 用 deepseek-chat 等

    # CORS — 允许的前端域名，逗号分隔
    # 开发环境：前端 Vite 默认在 5173 端口
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # pydantic-settings 配置：自动从 .env 文件读取
    # .env 文件应放在 backend/ 目录下（uvicorn 的工作目录）
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def cors_origins_list(self) -> list[str]:
        """将逗号分隔的 CORS_ORIGINS 字符串转为列表，供 FastAPI 中间件使用。"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


# 模块级单例 — 应用启动时创建一次，全局共享
settings = Settings()
