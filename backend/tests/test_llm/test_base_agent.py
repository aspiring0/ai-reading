"""
BaseAgent 测试 — 验证 system_prompt 管理、JSON 解析、重试逻辑。
"""

from unittest.mock import AsyncMock

import pytest
from pydantic import BaseModel

from app.agents.base import BaseAgent
from app.exceptions import ExternalServiceException


# 用 Sample 前缀避免 pytest 把它们当测试类收集
class SampleResult(BaseModel):
    """测试用的简单结果类型。"""

    title: str
    score: float


class SampleAgent(BaseAgent):
    """测试用的 Agent 子类。"""

    system_prompt = "You are a test assistant."


@pytest.fixture
def agent() -> SampleAgent:
    """提供一个 SampleAgent（mock 掉 LLM）。"""
    a = SampleAgent()
    a.llm = AsyncMock()
    return a


class TestBaseAgentCallLlmJson:
    """测试 call_llm_json 方法。"""

    @pytest.mark.asyncio
    async def test_successful_json_parse(self, agent: SampleAgent):
        """LLM 返回合法 JSON，正确解析为 Pydantic 模型。"""
        agent.llm.chat_json.return_value = '{"title": "Hello", "score": 0.9}'

        result = await agent.call_llm_json("test prompt", result_type=SampleResult)

        assert isinstance(result, SampleResult)
        assert result.title == "Hello"
        assert result.score == 0.9

    @pytest.mark.asyncio
    async def test_passes_system_prompt(self, agent: SampleAgent):
        """验证 system_prompt 被传给 LLM。"""
        agent.llm.chat_json.return_value = '{"title": "x", "score": 0.5}'

        await agent.call_llm_json("test", result_type=SampleResult)

        call_kwargs = agent.llm.chat_json.call_args[1]
        assert call_kwargs["system_prompt"] == "You are a test assistant."
        assert call_kwargs["user_prompt"] == "test"

    @pytest.mark.asyncio
    async def test_invalid_json_retries(self, agent: SampleAgent):
        """第一次返回非法 JSON，重试后成功。"""
        agent.llm.chat_json.side_effect = [
            "not valid json {{{",
            '{"title": "Retry OK", "score": 0.8}',
        ]

        result = await agent.call_llm_json("test", result_type=SampleResult, max_retries=1)
        assert result.title == "Retry OK"

    @pytest.mark.asyncio
    async def test_missing_field_retries(self, agent: SampleAgent):
        """JSON 合法但缺少必要字段，重试。"""
        agent.llm.chat_json.side_effect = [
            '{"title": "Missing score"}',  # 缺 score 字段
            '{"title": "Complete", "score": 0.7}',
        ]

        result = await agent.call_llm_json("test", result_type=SampleResult, max_retries=1)
        assert result.score == 0.7

    @pytest.mark.asyncio
    async def test_all_retries_fail(self, agent: SampleAgent):
        """所有重试都返回非法 JSON，抛 ExternalServiceException。"""
        agent.llm.chat_json.return_value = "not json at all"

        with pytest.raises(ExternalServiceException, match="Failed to parse"):
            await agent.call_llm_json("test", result_type=SampleResult, max_retries=2)

    @pytest.mark.asyncio
    async def test_retry_adds_error_hint(self, agent: SampleAgent):
        """重试时在 prompt 里加上错误提示。"""
        agent.llm.chat_json.side_effect = [
            "bad json",
            '{"title": "Fixed", "score": 1.0}',
        ]

        await agent.call_llm_json("original prompt", result_type=SampleResult, max_retries=1)

        # 第二次调用的 user_prompt 应包含错误提示
        second_call = agent.llm.chat_json.call_args_list[1]
        assert "JSON" in second_call[1]["user_prompt"]
        assert "original prompt" in second_call[1]["user_prompt"]
