"""
LLM Client 测试 — 验证重试逻辑、超时处理、JSON 解析。

Mock openai.AsyncOpenAI，不调用真实 API。
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions import ExternalServiceException
from app.utils.llm_client import LLMClient


def _mock_completion(content: str) -> MagicMock:
    """构造一个假的 OpenAI completion 响应。"""
    choice = MagicMock()
    choice.message.content = content
    response = MagicMock()
    response.choices = [choice]
    response.usage.total_tokens = 100
    return response


@pytest.fixture
def llm_client() -> LLMClient:
    """提供一个 LLMClient 实例（mock 掉 OpenAI 客户端）。"""
    client = LLMClient()
    client.client = AsyncMock()
    return client


class TestLLMClientChat:
    """测试 chat() 基础调用。"""

    @pytest.mark.asyncio
    async def test_successful_call(self, llm_client: LLMClient):
        """正常调用返回文本。"""
        llm_client.client.chat.completions.create.return_value = _mock_completion("Hello!")

        result = await llm_client.chat("system", "user")
        assert result == "Hello!"

    @pytest.mark.asyncio
    async def test_passes_correct_params(self, llm_client: LLMClient):
        """验证传递给 OpenAI SDK 的参数正确。"""
        llm_client.client.chat.completions.create.return_value = _mock_completion("ok")

        await llm_client.chat("sys prompt", "user prompt", temperature=0.5, max_tokens=100)

        call_kwargs = llm_client.client.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == llm_client.model
        assert call_kwargs["messages"][0]["role"] == "system"
        assert call_kwargs["messages"][0]["content"] == "sys prompt"
        assert call_kwargs["messages"][1]["content"] == "user prompt"
        assert call_kwargs["temperature"] == 0.5
        assert call_kwargs["max_tokens"] == 100


class TestLLMClientRetry:
    """测试重试逻辑（指数退避）。"""

    @pytest.mark.asyncio
    async def test_retry_on_failure(self, llm_client: LLMClient):
        """第一次失败，第二次成功。"""
        llm_client.client.chat.completions.create.side_effect = [
            Exception("Temporary error"),
            _mock_completion("Success on retry"),
        ]

        result = await llm_client.chat("sys", "user", max_retries=3)
        assert result == "Success on retry"
        assert llm_client.client.chat.completions.create.call_count == 2

    @pytest.mark.asyncio
    async def test_all_retries_exhausted(self, llm_client: LLMClient):
        """所有重试都失败，抛 ExternalServiceException。"""
        llm_client.client.chat.completions.create.side_effect = Exception("Always fails")

        with pytest.raises(ExternalServiceException, match="failed after 2 attempts"):
            await llm_client.chat("sys", "user", max_retries=2)

    @pytest.mark.asyncio
    async def test_retry_count_correct(self, llm_client: LLMClient):
        """验证实际调用次数等于 max_retries。"""
        llm_client.client.chat.completions.create.side_effect = Exception("fail")

        with pytest.raises(ExternalServiceException):
            await llm_client.chat("sys", "user", max_retries=3)

        assert llm_client.client.chat.completions.create.call_count == 3


class TestLLMClientChatJson:
    """测试 chat_json() 方法。"""

    @pytest.mark.asyncio
    async def test_passes_json_format(self, llm_client: LLMClient):
        """chat_json 应传 response_format={"type": "json_object"}。"""
        llm_client.client.chat.completions.create.return_value = _mock_completion('{"key": "value"}')

        await llm_client.chat_json("sys", "user")
        call_kwargs = llm_client.client.chat.completions.create.call_args[1]
        assert call_kwargs["response_format"] == {"type": "json_object"}
