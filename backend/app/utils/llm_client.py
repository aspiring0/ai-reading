"""
LLM 客户端 — 封装 OpenAI SDK，提供统一调用接口。

为什么封装一层：
    1. 配置集中管理（base_url、model 从 settings 读取）
    2. 自动重试（指数退避，处理 429 限流和临时错误）
    3. 日志记录（每次调用记录 token 用量和耗时）
    4. 方便测试（mock 这个类即可，不用 mock openai SDK）

使用方式：
    client = LLMClient()
    result = await client.chat("你是一个助手", "你好")
"""

import asyncio
import logging
import time

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """异步 LLM 客户端 — 封装 OpenAI SDK，自带重试和日志。"""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
        self.model = settings.OPENAI_MODEL
        self.default_max_retries = 3
        self.default_timeout = 30.0

    async def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        response_format: dict | None = None,
        max_retries: int | None = None,
    ) -> str:
        """调用 LLM 并返回文本响应，带指数退避重试。

        Args:
            system_prompt: 系统提示词（定义角色和行为）
            user_prompt: 用户消息（具体任务）
            temperature: 随机性（0-2，越高越随机）
            max_tokens: 最大生成 token 数
            response_format: 响应格式，如 {"type": "json_object"}
            max_retries: 最大重试次数

        Returns:
            LLM 返回的文本内容

        Raises:
            ExternalServiceException: 重试耗尽后仍失败
        """
        retries = max_retries or self.default_max_retries
        last_error = None

        for attempt in range(retries):
            start_time = time.time()
            try:
                kwargs: dict = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": temperature,
                    "timeout": self.default_timeout,
                }
                if max_tokens:
                    kwargs["max_tokens"] = max_tokens
                if response_format:
                    kwargs["response_format"] = response_format

                response = await self.client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content or ""

                # 记录调用信息
                duration_ms = int((time.time() - start_time) * 1000)
                usage = response.usage
                logger.info(
                    f"LLM call: model={self.model}, "
                    f"tokens={usage.total_tokens if usage else 'N/A'}, "
                    f"duration={duration_ms}ms, "
                    f"attempt={attempt + 1}/{retries}"
                )

                return content

            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                last_error = e
                logger.warning(
                    f"LLM call failed: attempt={attempt + 1}/{retries}, "
                    f"error={type(e).__name__}: {e}, duration={duration_ms}ms"
                )

                if attempt < retries - 1:
                    # 指数退避：1s, 2s, 4s...
                    wait = 2**attempt
                    logger.info(f"Retrying in {wait}s...")
                    await asyncio.sleep(wait)

        # 所有重试都失败了
        from app.exceptions import ExternalServiceException

        raise ExternalServiceException(
            f"LLM call failed after {retries} attempts: {last_error}"
        )

    async def chat_json(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        max_retries: int | None = None,
    ) -> str:
        """调用 LLM 并期望返回 JSON 格式。

        等价于 chat() 加上 response_format={"type": "json_object"}。
        """
        return await self.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            max_retries=max_retries,
        )
