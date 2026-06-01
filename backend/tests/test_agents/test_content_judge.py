"""
ContentJudge 测试 — 验证内容评估 Agent 的行为。

测试策略：
    - Mock 掉 LLM 调用（agent.llm.chat_json）
    - 验证评估结果解析（通过/失败）
    - 验证 system_prompt 包含评估角色和维度关键词
    - 验证 user_prompt 包含文章标题和内容
    - 验证 score 为 4 个维度的平均值
"""

import json
from unittest.mock import AsyncMock

import pytest

from app.agents.content_generator import GeneratedSegment, GenerationResult

# ---- Mock LLM 返回的 JSON ----

MOCK_PASS_JSON = json.dumps(
    {
        "score": 0.85,
        "dimensions": {
            "grammar": 0.9,
            "vocabulary": 0.8,
            "coherence": 0.85,
            "engagement": 0.85,
        },
        "passed": True,
        "feedback": "",
    }
)

MOCK_FAIL_JSON = json.dumps(
    {
        "score": 0.55,
        "dimensions": {
            "grammar": 0.5,
            "vocabulary": 0.6,
            "coherence": 0.5,
            "engagement": 0.6,
        },
        "passed": False,
        "feedback": "Grammar errors in tenses. Vocabulary is repetitive.",
    }
)


def _make_draft() -> GenerationResult:
    """构造一个测试用的 GenerationResult。"""
    return GenerationResult(
        title="Test Article",
        segments=[
            GeneratedSegment(
                segment_index=0, segment_type="heading", content="Intro"
            ),
            GeneratedSegment(
                segment_index=1,
                segment_type="paragraph",
                content="This is paragraph one.",
            ),
        ],
        word_count=10,
        cefr_level="B1",
        difficulty="medium",
    )


@pytest.fixture
def agent():
    """提供一个 ContentJudge 实例（mock 掉 LLM）。"""
    from app.agents.content_judge import ContentJudge

    a = ContentJudge()
    a.llm = AsyncMock()
    return a


class TestContentJudgeJudge:
    """测试 ContentJudge.judge 方法。"""

    @pytest.mark.asyncio
    async def test_judge_pass_returns_judge_result(self, agent):
        """评估通过时返回 passed=True, score=0.85 的 JudgeResult。"""
        from app.agents.content_judge import JudgeResult

        agent.llm.chat_json.return_value = MOCK_PASS_JSON

        result = await agent.judge(_make_draft())

        assert isinstance(result, JudgeResult)
        assert result.passed is True
        assert result.score == 0.85

    @pytest.mark.asyncio
    async def test_judge_fail_returns_feedback(self, agent):
        """评估未通过时返回 passed=False 和非空 feedback。"""
        agent.llm.chat_json.return_value = MOCK_FAIL_JSON

        result = await agent.judge(_make_draft())

        assert result.passed is False
        assert result.feedback != ""
        assert "Grammar errors" in result.feedback

    @pytest.mark.asyncio
    async def test_judge_passes_system_prompt(self, agent):
        """system_prompt 包含 evaluator 和 grammar 关键词。"""
        agent.llm.chat_json.return_value = MOCK_PASS_JSON

        await agent.judge(_make_draft())

        call_kwargs = agent.llm.chat_json.call_args[1]
        system_prompt = call_kwargs["system_prompt"]
        assert "evaluator" in system_prompt
        assert "grammar" in system_prompt

    @pytest.mark.asyncio
    async def test_judge_passes_article_content(self, agent):
        """user_prompt 包含文章标题和段落内容。"""
        agent.llm.chat_json.return_value = MOCK_PASS_JSON

        await agent.judge(_make_draft())

        call_kwargs = agent.llm.chat_json.call_args[1]
        user_prompt = call_kwargs["user_prompt"]
        assert "Test Article" in user_prompt
        assert "This is paragraph one." in user_prompt

    @pytest.mark.asyncio
    async def test_judge_dimensions_sum_to_score(self, agent):
        """score 应等于 4 个维度的平均值。"""
        agent.llm.chat_json.return_value = MOCK_PASS_JSON

        result = await agent.judge(_make_draft())

        dims = result.dimensions
        expected = (dims.grammar + dims.vocabulary + dims.coherence + dims.engagement) / 4
        assert result.score == pytest.approx(expected, abs=1e-9)
