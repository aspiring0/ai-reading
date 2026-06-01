"""
ContentGenerator 测试 — 验证文章生成 Agent 的行为。

测试策略：
    - Mock 掉 LLM 调用（agent.llm.chat_json）
    - 验证生成结果解析
    - 验证 system_prompt 内容
    - 验证 user_prompt 中包含 topic / difficulty / word_count
    - 验证可选参数 custom_instructions / previous_feedback 的注入
"""

import json
from unittest.mock import AsyncMock

import pytest

from app.agents.content_generator import ContentGenerator, GenerationResult

# LLM mock 返回的合法 JSON
MOCK_LLM_RESPONSE = json.dumps(
    {
        "title": "The Impact of Climate Change",
        "segments": [
            {"segment_index": 0, "segment_type": "heading", "content": "Introduction"},
            {
                "segment_index": 1,
                "segment_type": "paragraph",
                "content": "Climate change affects us all.",
            },
            {"segment_index": 2, "segment_type": "heading", "content": "Solutions"},
            {
                "segment_index": 3,
                "segment_type": "paragraph",
                "content": "We must act now to reduce emissions.",
            },
        ],
        "word_count": 15,
        "cefr_level": "B1",
        "difficulty": "medium",
    }
)


@pytest.fixture
def agent() -> ContentGenerator:
    """提供一个 ContentGenerator 实例（mock 掉 LLM）。"""
    a = ContentGenerator()
    a.llm = AsyncMock()
    return a


class TestContentGeneratorGenerate:
    """测试 ContentGenerator.generate 方法。"""

    @pytest.mark.asyncio
    async def test_generate_returns_generation_result(self, agent: ContentGenerator):
        """generate 返回正确的 GenerationResult 对象。"""
        agent.llm.chat_json.return_value = MOCK_LLM_RESPONSE

        result = await agent.generate(
            topic="climate change",
            difficulty="medium",
            target_word_count=200,
        )

        assert isinstance(result, GenerationResult)
        assert result.title == "The Impact of Climate Change"
        assert len(result.segments) == 4
        assert result.segments[0].segment_index == 0
        assert result.segments[0].segment_type == "heading"
        assert result.segments[1].content == "Climate change affects us all."
        assert result.word_count == 15
        assert result.cefr_level == "B1"
        assert result.difficulty == "medium"

    @pytest.mark.asyncio
    async def test_generate_passes_system_prompt(self, agent: ContentGenerator):
        """system_prompt 包含 English learning content writer 角色描述。"""
        agent.llm.chat_json.return_value = MOCK_LLM_RESPONSE

        await agent.generate(
            topic="climate change",
            difficulty="medium",
            target_word_count=200,
        )

        call_kwargs = agent.llm.chat_json.call_args[1]
        assert "English learning content writer" in call_kwargs["system_prompt"]

    @pytest.mark.asyncio
    async def test_generate_passes_topic_and_difficulty(self, agent: ContentGenerator):
        """user_prompt 包含 topic、difficulty 和 target_word_count。"""
        agent.llm.chat_json.return_value = MOCK_LLM_RESPONSE

        await agent.generate(
            topic="artificial intelligence",
            difficulty="hard",
            target_word_count=300,
        )

        call_kwargs = agent.llm.chat_json.call_args[1]
        user_prompt = call_kwargs["user_prompt"]
        assert "artificial intelligence" in user_prompt
        assert "hard" in user_prompt
        assert "300" in user_prompt

    @pytest.mark.asyncio
    async def test_generate_injects_custom_instructions(self, agent: ContentGenerator):
        """user_prompt 包含 custom_instructions 内容。"""
        agent.llm.chat_json.return_value = MOCK_LLM_RESPONSE

        await agent.generate(
            topic="climate change",
            difficulty="medium",
            target_word_count=200,
            custom_instructions="Include a vocabulary list at the end.",
        )

        call_kwargs = agent.llm.chat_json.call_args[1]
        user_prompt = call_kwargs["user_prompt"]
        assert "Include a vocabulary list at the end." in user_prompt

    @pytest.mark.asyncio
    async def test_generate_injects_previous_feedback(self, agent: ContentGenerator):
        """user_prompt 包含 previous_feedback 和 'previous version' 引用。"""
        agent.llm.chat_json.return_value = MOCK_LLM_RESPONSE

        await agent.generate(
            topic="climate change",
            difficulty="medium",
            target_word_count=200,
            previous_feedback="The article was too short and lacked examples.",
        )

        call_kwargs = agent.llm.chat_json.call_args[1]
        user_prompt = call_kwargs["user_prompt"]
        assert "The article was too short and lacked examples." in user_prompt
        assert "previous version" in user_prompt

    @pytest.mark.asyncio
    async def test_generate_without_optional_params(self, agent: ContentGenerator):
        """不带可选参数时 generate 正常工作。"""
        agent.llm.chat_json.return_value = MOCK_LLM_RESPONSE

        result = await agent.generate(
            topic="technology",
            difficulty="easy",
            target_word_count=150,
        )

        assert isinstance(result, GenerationResult)
        assert result.title == "The Impact of Climate Change"
