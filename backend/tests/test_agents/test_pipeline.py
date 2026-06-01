"""
Pipeline orchestration 测试 — 验证 ArticleService.generate_with_pipeline 的行为。

测试策略：
    - Mock 掉 ContentGenerator 和 ContentJudge（在 article_service 模块中使用 patch）
    - 验证生成-评估-重试循环逻辑
    - 验证元数据包含完整信息
"""

from unittest.mock import AsyncMock, patch

import pytest

from app.agents.content_generator import GeneratedSegment, GenerationResult
from app.agents.content_judge import JudgeDimensions, JudgeResult
from app.config import settings
from app.services.article_service import ArticleService


def _make_draft(**overrides) -> GenerationResult:
    """构建一个模拟的 GenerationResult。"""
    defaults = {
        "title": "The Rise of Artificial Intelligence",
        "segments": [
            GeneratedSegment(segment_index=0, segment_type="heading", content="Introduction"),
            GeneratedSegment(
                segment_index=1,
                segment_type="paragraph",
                content="Artificial intelligence is transforming every industry.",
            ),
        ],
        "word_count": 8,
        "cefr_level": "B1",
        "difficulty": "medium",
    }
    defaults.update(overrides)
    return GenerationResult(**defaults)


def _make_judge_result(score: float, passed: bool, feedback: str = "") -> JudgeResult:
    """构建一个模拟的 JudgeResult。"""
    return JudgeResult(
        score=score,
        dimensions=JudgeDimensions(
            grammar=score,
            vocabulary=score,
            coherence=score,
            engagement=score,
        ),
        passed=passed,
        feedback=feedback,
    )


class TestGenerateWithPipeline:
    """测试 ArticleService.generate_with_pipeline 管线编排。"""

    @pytest.mark.asyncio
    async def test_pipeline_passes_first_attempt(self):
        """第一次生成即通过 — generator 调用 1 次，judge 调用 1 次。"""
        draft = _make_draft()
        judge_result = _make_judge_result(score=0.85, passed=True, feedback="Good article.")

        mock_gen = AsyncMock()
        mock_gen.generate.return_value = draft
        mock_judge = AsyncMock()
        mock_judge.judge.return_value = judge_result

        with (
            patch("app.services.article_service.ContentGenerator", return_value=mock_gen),
            patch("app.services.article_service.ContentJudge", return_value=mock_judge),
        ):
            service = ArticleService(session=AsyncMock(), redis=None)
            result = await service.generate_with_pipeline(
                topic="AI",
                difficulty="medium",
                target_word_count=300,
            )

        assert result["attempts"] == 1
        assert result["passed"] is True
        assert result["quality_score"] == 0.85
        mock_gen.generate.assert_called_once()
        mock_judge.judge.assert_called_once()

    @pytest.mark.asyncio
    async def test_pipeline_retries_on_fail_then_passes(self):
        """第一次失败、第二次通过 — generator 调用 2 次，judge 调用 2 次。"""
        draft = _make_draft()
        fail_result = _make_judge_result(score=0.5, passed=False, feedback="Improve vocabulary diversity.")
        pass_result = _make_judge_result(score=0.80, passed=True, feedback="Much better.")

        mock_gen = AsyncMock()
        mock_gen.generate.return_value = draft
        mock_judge = AsyncMock()
        mock_judge.judge.side_effect = [fail_result, pass_result]

        with (
            patch("app.services.article_service.ContentGenerator", return_value=mock_gen),
            patch("app.services.article_service.ContentJudge", return_value=mock_judge),
        ):
            service = ArticleService(session=AsyncMock(), redis=None)
            result = await service.generate_with_pipeline(
                topic="AI",
                difficulty="medium",
                target_word_count=300,
            )

        assert result["attempts"] == 2
        assert result["passed"] is True
        assert result["quality_score"] == 0.80

        # generator 被调用了 2 次
        assert mock_gen.generate.call_count == 2
        # judge 被调用了 2 次
        assert mock_judge.judge.call_count == 2

        # 第二次 generate 调用应包含 previous_feedback
        second_call_kwargs = mock_gen.generate.call_args_list[1]
        assert second_call_kwargs[1]["previous_feedback"] == "Improve vocabulary diversity."

    @pytest.mark.asyncio
    async def test_pipeline_max_retries_stores_last_result(self):
        """3 次都失败 — 返回最后一次结果，passed=False，attempts=3。"""
        draft = _make_draft()
        fail_result = _make_judge_result(score=0.5, passed=False, feedback="Needs work.")

        mock_gen = AsyncMock()
        mock_gen.generate.return_value = draft
        mock_judge = AsyncMock()
        mock_judge.judge.return_value = fail_result

        with (
            patch("app.services.article_service.ContentGenerator", return_value=mock_gen),
            patch("app.services.article_service.ContentJudge", return_value=mock_judge),
        ):
            service = ArticleService(session=AsyncMock(), redis=None)
            result = await service.generate_with_pipeline(
                topic="AI",
                difficulty="medium",
                target_word_count=300,
            )

        assert result["attempts"] == 3
        assert result["passed"] is False
        assert result["quality_score"] == 0.5
        assert mock_gen.generate.call_count == 3
        assert mock_judge.judge.call_count == 3

    @pytest.mark.asyncio
    async def test_metadata_contains_attempts_and_score(self):
        """generation_metadata 包含 model、attempts、final_score、passed、dimensions 等。"""
        draft = _make_draft(word_count=295)
        judge_result = _make_judge_result(score=0.85, passed=True, feedback="Great.")

        mock_gen = AsyncMock()
        mock_gen.generate.return_value = draft
        mock_judge = AsyncMock()
        mock_judge.judge.return_value = judge_result

        with (
            patch("app.services.article_service.ContentGenerator", return_value=mock_gen),
            patch("app.services.article_service.ContentJudge", return_value=mock_judge),
        ):
            service = ArticleService(session=AsyncMock(), redis=None)
            result = await service.generate_with_pipeline(
                topic="AI",
                difficulty="medium",
                target_word_count=300,
            )

        metadata = result["generation_metadata"]

        assert metadata["model"] == settings.OPENAI_MODEL
        assert metadata["attempts"] == 1
        assert metadata["final_score"] == 0.85
        assert metadata["passed"] is True
        assert metadata["target_word_count"] == 300
        assert metadata["actual_word_count"] == 295
        assert "dimensions" in metadata
        assert metadata["dimensions"]["grammar"] == 0.85
        assert metadata["dimensions"]["vocabulary"] == 0.85
        assert metadata["dimensions"]["coherence"] == 0.85
        assert metadata["dimensions"]["engagement"] == 0.85
