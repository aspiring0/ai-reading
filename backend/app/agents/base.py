"""
Agent 基类 — 所有 LLM Agent 的父类。

提供：
    1. system_prompt 模板管理
    2. LLM 调用 + JSON 解析 + 重试
    3. 返回类型化的 Pydantic Result 对象

子类只需：
    - 设置 system_prompt
    - 实现 run() 方法（定义输入参数和输出类型）
"""

import json
import logging
from typing import TypeVar

from pydantic import BaseModel

from app.utils.llm_client import LLMClient

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class BaseAgent:
    """LLM Agent 基类 — 子类继承此类获得 LLM 调用能力。"""

    system_prompt: str = ""  # 子类必须覆盖

    def __init__(self, llm_client: LLMClient | None = None):
        self.llm = llm_client or LLMClient()

    async def call_llm_json(
        self,
        user_prompt: str,
        *,
        result_type: type[T],
        temperature: float = 0.7,
        max_retries: int = 2,
    ) -> T:
        """调用 LLM，期望返回 JSON，解析为 Pydantic 模型。

        流程：
            1. 调用 llm.chat_json()
            2. 解析 JSON
            3. 用 Pydantic 校验并转为 result_type
            4. 失败则重试（JSON 格式错误或字段缺失）

        Args:
            user_prompt: 给 LLM 的具体任务描述
            result_type: 期望返回的 Pydantic 模型类
            temperature: 随机性
            max_retries: JSON 解析失败的重试次数

        Returns:
            解析成功的 result_type 实例
        """
        last_error = None

        for attempt in range(max_retries + 1):
            raw = await self.llm.chat_json(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
            )

            try:
                parsed = json.loads(raw)
                return result_type.model_validate(parsed)
            except (json.JSONDecodeError, ValueError) as e:
                last_error = e
                logger.warning(
                    f"Agent JSON parse failed (attempt {attempt + 1}/{max_retries + 1}): {e}"
                )
                if attempt < max_retries:
                    # 在 user_prompt 里加上错误提示，帮助 LLM 纠正
                    user_prompt = (
                        f"{user_prompt}\n\n"
                        f"上次返回的 JSON 格式有误：{e}\n"
                        f"请确保返回合法 JSON。"
                    )

        # 所有重试都失败
        from app.exceptions import ExternalServiceException

        raise ExternalServiceException(
            f"Failed to parse LLM response as {result_type.__name__} "
            f"after {max_retries + 1} attempts: {last_error}"
        )
