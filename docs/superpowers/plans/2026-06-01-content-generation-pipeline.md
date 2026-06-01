# Content Generation Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement ContentGenerator and ContentJudge LLM agents with a retry pipeline that generates, evaluates, and stores English learning articles.

**Architecture:** Two Agent classes inherit BaseAgent (which handles LLM calls + JSON parsing). ArticleService orchestrates them in a generate→judge→retry loop (max 3 attempts). All LLM calls are mocked in tests.

**Tech Stack:** Python 3.11+, Pydantic v2, pytest + pytest-asyncio, unittest.mock

---

## File Structure

| Action | File | Responsibility |
|---|---|---|
| Create | `backend/app/agents/content_generator.py` | ContentGenerator Agent + Pydantic result models |
| Create | `backend/app/agents/content_judge.py` | ContentJudge Agent + Pydantic result models |
| Modify | `backend/app/services/article_service.py` | Add `generate_with_pipeline()` method |
| Create | `backend/tests/test_agents/test_content_generator.py` | ContentGenerator unit tests |
| Create | `backend/tests/test_agents/test_content_judge.py` | ContentJudge unit tests |
| Create | `backend/tests/test_agents/test_pipeline.py` | Pipeline integration tests (mock both agents) |
| Create | `backend/tests/test_agents/__init__.py` | Package init |

---

### Task 1: ContentGenerator Agent — Tests

**Files:**
- Create: `backend/tests/test_agents/__init__.py`
- Create: `backend/tests/test_agents/test_content_generator.py`

- [ ] **Step 1: Create test file with all ContentGenerator tests**

```python
"""
ContentGenerator Agent 测试 — 验证文章生成和反馈注入。
所有 LLM 调用通过 mock，不调用真实 API。
"""

import json
from unittest.mock import AsyncMock

import pytest

from app.agents.content_generator import ContentGenerator, GenerationResult


# LLM 返回的模拟 JSON
MOCK_GENERATION_JSON = json.dumps({
    "title": "The Impact of Climate Change",
    "segments": [
        {"segment_index": 0, "segment_type": "heading", "content": "Introduction"},
        {"segment_index": 1, "segment_type": "paragraph", "content": "Climate change affects us all."},
        {"segment_index": 2, "segment_type": "heading", "content": "Solutions"},
        {"segment_index": 3, "segment_type": "paragraph", "content": "We must act now to reduce emissions."},
    ],
    "word_count": 15,
    "cefr_level": "B1",
    "difficulty": "medium",
})


@pytest.fixture
def generator() -> ContentGenerator:
    """提供一个 ContentGenerator（mock 掉 LLM）。"""
    gen = ContentGenerator()
    gen.llm = AsyncMock()
    return gen


class TestContentGenerator:
    @pytest.mark.asyncio
    async def test_generate_returns_generation_result(self, generator: ContentGenerator):
        """生成成功返回 GenerationResult。"""
        generator.llm.chat_json.return_value = MOCK_GENERATION_JSON

        result = await generator.generate(
            topic="climate change",
            difficulty="medium",
            target_word_count=300,
        )

        assert isinstance(result, GenerationResult)
        assert result.title == "The Impact of Climate Change"
        assert len(result.segments) == 4
        assert result.segments[0].segment_type == "heading"
        assert result.cefr_level == "B1"

    @pytest.mark.asyncio
    async def test_generate_passes_system_prompt(self, generator: ContentGenerator):
        """验证 system_prompt 被传给 LLM。"""
        generator.llm.chat_json.return_value = MOCK_GENERATION_JSON

        await generator.generate(topic="AI", difficulty="easy", target_word_count=200)

        call_kwargs = generator.llm.chat_json.call_args[1]
        assert "English learning content writer" in call_kwargs["system_prompt"]

    @pytest.mark.asyncio
    async def test_generate_passes_topic_and_difficulty(self, generator: ContentGenerator):
        """验证 topic 和 difficulty 出现在 user_prompt 里。"""
        generator.llm.chat_json.return_value = MOCK_GENERATION_JSON

        await generator.generate(topic="AI ethics", difficulty="hard", target_word_count=400)

        call_kwargs = generator.llm.chat_json.call_args[1]
        assert "AI ethics" in call_kwargs["user_prompt"]
        assert "hard" in call_kwargs["user_prompt"]
        assert "400" in call_kwargs["user_prompt"]

    @pytest.mark.asyncio
    async def test_generate_injects_custom_instructions(self, generator: ContentGenerator):
        """自定义指令被注入到 user_prompt。"""
        generator.llm.chat_json.return_value = MOCK_GENERATION_JSON

        await generator.generate(
            topic="AI",
            difficulty="easy",
            target_word_count=200,
            custom_instructions="Focus on beginner-friendly examples",
        )

        call_kwargs = generator.llm.chat_json.call_args[1]
        assert "beginner-friendly examples" in call_kwargs["user_prompt"]

    @pytest.mark.asyncio
    async def test_generate_injects_previous_feedback(self, generator: ContentGenerator):
        """Judge 反馈被注入到重试的 user_prompt。"""
        generator.llm.chat_json.return_value = MOCK_GENERATION_JSON

        await generator.generate(
            topic="AI",
            difficulty="easy",
            target_word_count=200,
            previous_feedback="Grammar errors in paragraph 2. Vocabulary too simple.",
        )

        call_kwargs = generator.llm.chat_json.call_args[1]
        assert "Grammar errors" in call_kwargs["user_prompt"]
        assert "previous version" in call_kwargs["user_prompt"].lower()

    @pytest.mark.asyncio
    async def test_generate_without_optional_params(self, generator: ContentGenerator):
        """不传可选参数时正常工作。"""
        generator.llm.chat_json.return_value = MOCK_GENERATION_JSON

        result = await generator.generate(topic="Science", difficulty="easy", target_word_count=100)

        assert isinstance(result, GenerationResult)
        call_kwargs = generator.llm.chat_json.call_args[1]
        assert "Additional instructions" not in call_kwargs["user_prompt"]
        assert "previous version" not in call_kwargs["user_prompt"].lower()
```

- [ ] **Step 2: Run tests — should FAIL (module not found)**

Run: `cd backend && python -m pytest tests/test_agents/test_content_generator.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.agents.content_generator'`

- [ ] **Step 3: Commit the failing test**

```bash
git add backend/tests/test_agents/
git commit -m "test(agents): add ContentGenerator unit tests (failing)"
```

---

### Task 2: ContentGenerator Agent — Implementation

**Files:**
- Create: `backend/app/agents/content_generator.py`

- [ ] **Step 1: Write ContentGenerator implementation**

```python
"""
ContentGenerator Agent — 让 LLM 生成英语学习文章。

接收 topic + difficulty，返回结构化的文章（标题+段落+元信息）。
继承 BaseAgent，自动处理 JSON 解析和重试。
"""

from app.agents.base import BaseAgent
from pydantic import BaseModel


class GeneratedSegment(BaseModel):
    """生成文章的一个段落。"""
    segment_index: int
    segment_type: str  # heading / paragraph
    content: str


class GenerationResult(BaseModel):
    """ContentGenerator 的输出 — 一篇完整的结构化文章。"""
    title: str
    segments: list[GeneratedSegment]
    word_count: int
    cefr_level: str  # A1-C2
    difficulty: str


class ContentGenerator(BaseAgent):
    """内容生成 Agent — 调用 LLM 生成英语阅读文章。"""

    system_prompt = (
        "You are an expert English learning content writer. "
        "Generate engaging reading materials for English learners.\n\n"
        "Rules:\n"
        "- Match the requested difficulty level in vocabulary and sentence complexity\n"
        "- Easy: simple sentences, common words (CEFR A1-A2)\n"
        "- Medium: varied sentences, some academic vocabulary (CEFR B1-B2)\n"
        "- Hard: complex sentences, advanced vocabulary (CEFR C1-C2)\n"
        "- Structure the article with headings and paragraphs\n"
        "- Target approximately the requested word count\n"
        "- Content must be factual and educational\n"
        "- Always respond with valid JSON matching the expected schema"
    )

    async def generate(
        self,
        topic: str,
        difficulty: str,
        target_word_count: int,
        custom_instructions: str | None = None,
        previous_feedback: str | None = None,
    ) -> GenerationResult:
        """生成一篇文章。

        Args:
            topic: 文章主题，如 "climate change"
            difficulty: easy / medium / hard
            target_word_count: 目标字数
            custom_instructions: 用户额外要求
            previous_feedback: Judge 的改进建议（重试时用）
        """
        user_prompt = (
            f"Topic: {topic}\n"
            f"Difficulty: {difficulty}\n"
            f"Target words: {target_word_count}"
        )

        if custom_instructions:
            user_prompt += f"\nAdditional instructions: {custom_instructions}"

        if previous_feedback:
            user_prompt += (
                f"\n\nThe previous version had these issues:\n"
                f"{previous_feedback}\n"
                f"Please address them in this new version."
            )

        return await self.call_llm_json(
            user_prompt=user_prompt,
            result_type=GenerationResult,
        )
```

- [ ] **Step 2: Run tests — should PASS**

Run: `cd backend && python -m pytest tests/test_agents/test_content_generator.py -v`
Expected: 6 passed

- [ ] **Step 3: Commit**

```bash
git add backend/app/agents/content_generator.py
git commit -m "feat(agents): add ContentGenerator agent with generation result models"
```

---

### Task 3: ContentJudge Agent — Tests

**Files:**
- Create: `backend/tests/test_agents/test_content_judge.py`

- [ ] **Step 1: Write ContentJudge tests**

```python
"""
ContentJudge Agent 测试 — 验证评分逻辑和反馈生成。
"""

import json
from unittest.mock import AsyncMock

import pytest

from app.agents.content_generator import GenerationResult, GeneratedSegment
from app.agents.content_judge import ContentJudge, JudgeResult


MOCK_PASS_JSON = json.dumps({
    "score": 0.85,
    "dimensions": {
        "grammar": 0.9,
        "vocabulary": 0.8,
        "coherence": 0.85,
        "engagement": 0.85,
    },
    "passed": True,
    "feedback": "",
})

MOCK_FAIL_JSON = json.dumps({
    "score": 0.55,
    "dimensions": {
        "grammar": 0.5,
        "vocabulary": 0.6,
        "coherence": 0.5,
        "engagement": 0.6,
    },
    "passed": False,
    "feedback": "Grammar errors in tenses. Vocabulary is repetitive. Paragraphs lack logical transitions.",
})


def _make_draft() -> GenerationResult:
    """构造一个测试用的 GenerationResult。"""
    return GenerationResult(
        title="Test Article",
        segments=[
            GeneratedSegment(segment_index=0, segment_type="heading", content="Intro"),
            GeneratedSegment(segment_index=1, segment_type="paragraph", content="This is paragraph one."),
        ],
        word_count=10,
        cefr_level="B1",
        difficulty="medium",
    )


@pytest.fixture
def judge() -> ContentJudge:
    """提供一个 ContentJudge（mock 掉 LLM）。"""
    j = ContentJudge()
    j.llm = AsyncMock()
    return j


class TestContentJudge:
    @pytest.mark.asyncio
    async def test_judge_pass_returns_judge_result(self, judge: ContentJudge):
        """评分通过返回正确的 JudgeResult。"""
        judge.llm.chat_json.return_value = MOCK_PASS_JSON

        result = await judge.judge(_make_draft())

        assert isinstance(result, JudgeResult)
        assert result.passed is True
        assert result.score == 0.85
        assert result.dimensions.grammar == 0.9

    @pytest.mark.asyncio
    async def test_judge_fail_returns_feedback(self, judge: ContentJudge):
        """评分未通过返回详细反馈。"""
        judge.llm.chat_json.return_value = MOCK_FAIL_JSON

        result = await judge.judge(_make_draft())

        assert result.passed is False
        assert result.score < 0.7
        assert len(result.feedback) > 0
        assert "Grammar" in result.feedback

    @pytest.mark.asyncio
    async def test_judge_passes_system_prompt(self, judge: ContentJudge):
        """验证 system_prompt 包含评估维度。"""
        judge.llm.chat_json.return_value = MOCK_PASS_JSON

        await judge.judge(_make_draft())

        call_kwargs = judge.llm.chat_json.call_args[1]
        assert "evaluator" in call_kwargs["system_prompt"].lower()
        assert "grammar" in call_kwargs["system_prompt"].lower()

    @pytest.mark.asyncio
    async def test_judge_passes_article_content(self, judge: ContentJudge):
        """验证文章内容被拼接到 user_prompt。"""
        judge.llm.chat_json.return_value = MOCK_PASS_JSON

        draft = _make_draft()
        await judge.judge(draft)

        call_kwargs = judge.llm.chat_json.call_args[1]
        assert draft.title in call_kwargs["user_prompt"]
        assert "This is paragraph one" in call_kwargs["user_prompt"]

    @pytest.mark.asyncio
    async def test_judge_dimensions_sum_to_score(self, judge: ContentJudge):
        """验证 score 是 dimensions 的平均值。"""
        judge.llm.chat_json.return_value = MOCK_PASS_JSON

        result = await judge.judge(_make_draft())

        expected_avg = (
            result.dimensions.grammar
            + result.dimensions.vocabulary
            + result.dimensions.coherence
            + result.dimensions.engagement
        ) / 4
        assert abs(result.score - expected_avg) < 0.01
```

- [ ] **Step 2: Run tests — should FAIL**

Run: `cd backend && python -m pytest tests/test_agents/test_content_judge.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.agents.content_judge'`

- [ ] **Step 3: Commit the failing test**

```bash
git add backend/tests/test_agents/test_content_judge.py
git commit -m "test(agents): add ContentJudge unit tests (failing)"
```

---

### Task 4: ContentJudge Agent — Implementation

**Files:**
- Create: `backend/app/agents/content_judge.py`

- [ ] **Step 1: Write ContentJudge implementation**

```python
"""
ContentJudge Agent — 让 LLM 评估文章质量。

接收生成的文章，从 4 个维度打分（语法、词汇、连贯性、吸引力），
返回评分和改进建议。
"""

from pydantic import BaseModel

from app.agents.base import BaseAgent
from app.agents.content_generator import GenerationResult


class JudgeDimensions(BaseModel):
    """评分的四个维度，每个 0-1。"""
    grammar: float
    vocabulary: float
    coherence: float
    engagement: float


class JudgeResult(BaseModel):
    """ContentJudge 的输出 — 文章质量评分。"""
    score: float  # 四维平均分
    dimensions: JudgeDimensions
    passed: bool  # score >= 0.7
    feedback: str  # 改进建议


class ContentJudge(BaseAgent):
    """内容评判 Agent — 调用 LLM 评估文章质量。"""

    system_prompt = (
        "You are an expert English education materials evaluator.\n"
        "Evaluate the given article on 4 dimensions (each 0.0 to 1.0):\n\n"
        "1. grammar: Are there grammatical errors? Are tenses used correctly?\n"
        "2. vocabulary: Is vocabulary diverse and appropriate for the difficulty?\n"
        "3. coherence: Do paragraphs flow logically? Is the structure clear?\n"
        "4. engagement: Would a learner find this interesting and motivating?\n\n"
        "Overall score = average of 4 dimensions.\n"
        "Pass threshold: 0.7\n\n"
        "If score < 0.7, provide specific, actionable feedback explaining "
        "what to improve. Be constructive, not just critical.\n"
        "Always respond with valid JSON matching the expected schema."
    )

    async def judge(self, draft: GenerationResult) -> JudgeResult:
        """评估一篇文章的质量。

        Args:
            draft: ContentGenerator 生成的文章

        Returns:
            JudgeResult 包含评分、维度分数、是否通过、反馈
        """
        full_text = "\n\n".join(seg.content for seg in draft.segments)

        user_prompt = (
            f"Evaluate this English learning article:\n"
            f"Title: {draft.title}\n"
            f"Difficulty: {draft.difficulty}\n"
            f"Word count: {draft.word_count}\n\n"
            f"Article content:\n{full_text}"
        )

        return await self.call_llm_json(
            user_prompt=user_prompt,
            result_type=JudgeResult,
        )
```

- [ ] **Step 2: Run tests — should PASS**

Run: `cd backend && python -m pytest tests/test_agents/test_content_judge.py -v`
Expected: 5 passed

- [ ] **Step 3: Commit**

```bash
git add backend/app/agents/content_judge.py
git commit -m "feat(agents): add ContentJudge agent with multi-dimension scoring"
```

---

### Task 5: Pipeline Orchestration — Tests

**Files:**
- Create: `backend/tests/test_agents/test_pipeline.py`

- [ ] **Step 1: Write pipeline tests**

```python
"""
Pipeline 管线测试 — 验证 generate→judge→retry 编排逻辑。

Mock 两个 Agent，测试正常路径、重试路径、最大重试路径。
"""

from unittest.mock import AsyncMock, patch

import pytest

from app.agents.content_generator import GenerationResult, GeneratedSegment
from app.agents.content_judge import JudgeResult, JudgeDimensions


def _make_draft(title: str = "Test") -> GenerationResult:
    """构造测试用 GenerationResult。"""
    return GenerationResult(
        title=title,
        segments=[
            GeneratedSegment(segment_index=0, segment_type="heading", content="Intro"),
            GeneratedSegment(segment_index=1, segment_type="paragraph", content="Body text."),
        ],
        word_count=10,
        cefr_level="B1",
        difficulty="medium",
    )


def _judge_pass(score: float = 0.85) -> JudgeResult:
    return JudgeResult(
        score=score,
        dimensions=JudgeDimensions(grammar=score, vocabulary=score, coherence=score, engagement=score),
        passed=True,
        feedback="",
    )


def _judge_fail(score: float = 0.5) -> JudgeResult:
    return JudgeResult(
        score=score,
        dimensions=JudgeDimensions(grammar=score, vocabulary=score, coherence=score, engagement=score),
        passed=False,
        feedback="Vocabulary too simple. Add more complex sentences.",
    )


class TestPipelineNormal:
    """管线正常路径：生成一次就通过。"""

    @pytest.mark.asyncio
    async def test_pipeline_passes_first_attempt(self):
        """一次通过，只调用 Generator 和 Judge 各一次。"""
        mock_gen = AsyncMock(return_value=_make_draft())
        mock_judge = AsyncMock(return_value=_judge_pass())

        with (
            patch("app.services.article_service.ContentGenerator", return_value=mock_gen),
            patch("app.services.article_service.ContentJudge", return_value=mock_judge),
        ):
            from app.services.article_service import ArticleService

            service = ArticleService(session=AsyncMock(), redis=None)
            result = await service.generate_with_pipeline(
                topic="AI", difficulty="medium", target_word_count=300
            )

        assert result["attempts"] == 1
        assert result["passed"] is True
        assert result["quality_score"] == 0.85
        mock_gen.generate.assert_called_once()
        mock_judge.judge.assert_called_once()


class TestPipelineRetry:
    """管线重试路径：第一次不通过，带反馈重试后通过。"""

    @pytest.mark.asyncio
    async def test_pipeline_retries_on_fail_then_passes(self):
        """第一次失败，第二次通过，共 2 次尝试。"""
        draft1 = _make_draft("Draft 1")
        draft2 = _make_draft("Draft 2 (improved)")

        mock_gen = AsyncMock(side_effect=[draft1, draft2])
        mock_judge = AsyncMock(side_effect=[_judge_fail(), _judge_pass()])

        with (
            patch("app.services.article_service.ContentGenerator", return_value=mock_gen),
            patch("app.services.article_service.ContentJudge", return_value=mock_judge),
        ):
            from app.services.article_service import ArticleService

            service = ArticleService(session=AsyncMock(), redis=None)
            result = await service.generate_with_pipeline(
                topic="Science", difficulty="easy", target_word_count=200
            )

        assert result["attempts"] == 2
        assert result["passed"] is True
        # 验证第二次生成收到了 feedback
        second_call = mock_gen.generate.call_args_list[1]
        assert second_call[1]["previous_feedback"] == "Vocabulary too simple. Add more complex sentences."

    @pytest.mark.asyncio
    async def test_pipeline_max_retries_stores_last_result(self):
        """3 次都不通过，存储最后一次结果。"""
        mock_gen = AsyncMock(return_value=_make_draft())
        mock_judge = AsyncMock(return_value=_judge_fail())

        with (
            patch("app.services.article_service.ContentGenerator", return_value=mock_gen),
            patch("app.services.article_service.ContentJudge", return_value=mock_judge),
        ):
            from app.services.article_service import ArticleService

            service = ArticleService(session=AsyncMock(), redis=None)
            result = await service.generate_with_pipeline(
                topic="History", difficulty="hard", target_word_count=400
            )

        assert result["attempts"] == 3
        assert result["passed"] is False
        assert result["quality_score"] == 0.5
        # 验证 Generator 被调用了 3 次
        assert mock_gen.generate.call_count == 3
        assert mock_judge.judge.call_count == 3


class TestPipelineMetadata:
    """验证 generation_metadata 内容。"""

    @pytest.mark.asyncio
    async def test_metadata_contains_attempts_and_score(self):
        """metadata 记录尝试次数、分数、模型名。"""
        mock_gen = AsyncMock(return_value=_make_draft())
        mock_judge = AsyncMock(return_value=_judge_pass(0.9))

        with (
            patch("app.services.article_service.ContentGenerator", return_value=mock_gen),
            patch("app.services.article_service.ContentJudge", return_value=mock_judge),
        ):
            from app.services.article_service import ArticleService

            service = ArticleService(session=AsyncMock(), redis=None)
            result = await service.generate_with_pipeline(
                topic="Tech", difficulty="medium", target_word_count=300
            )

        metadata = result["generation_metadata"]
        assert metadata["attempts"] == 1
        assert metadata["final_score"] == 0.9
        assert metadata["passed"] is True
        assert "model" in metadata
```

- [ ] **Step 2: Run tests — should FAIL**

Run: `cd backend && python -m pytest tests/test_agents/test_pipeline.py -v`
Expected: FAIL — `generate_with_pipeline` method doesn't exist

- [ ] **Step 3: Commit the failing test**

```bash
git add backend/tests/test_agents/test_pipeline.py
git commit -m "test(agents): add pipeline orchestration tests (failing)"
```

---

### Task 6: Pipeline Orchestration — Implementation

**Files:**
- Modify: `backend/app/services/article_service.py`

- [ ] **Step 1: Add imports and `generate_with_pipeline` method to ArticleService**

Add these imports at the top of `backend/app/services/article_service.py` (after existing imports):

```python
from app.agents.content_generator import ContentGenerator
from app.agents.content_judge import ContentJudge
```

Add this method to the `ArticleService` class (after existing methods):

```python
    async def generate_with_pipeline(
        self,
        topic: str,
        difficulty: str,
        target_word_count: int = 300,
        custom_instructions: str | None = None,
    ) -> dict:
        """生成管线：Generator → Judge → 不达标则带反馈重试（最多 3 次）。

        Returns:
            dict with article_id, quality_score, attempts, passed, generation_metadata
        """
        from app.config import settings

        generator = ContentGenerator()
        judge = ContentJudge()
        feedback = None
        attempts = 0
        last_judge_result = None
        draft = None

        for _ in range(3):
            attempts += 1
            draft = await generator.generate(
                topic=topic,
                difficulty=difficulty,
                target_word_count=target_word_count,
                custom_instructions=custom_instructions,
                previous_feedback=feedback,
            )
            last_judge_result = await judge.judge(draft)
            if last_judge_result.passed:
                break
            feedback = last_judge_result.feedback

        # 构造 generation_metadata
        metadata = {
            "model": settings.OPENAI_MODEL,
            "source": "ai_generated",
            "attempts": attempts,
            "passed": last_judge_result.passed,
            "final_score": last_judge_result.score,
            "dimensions": last_judge_result.dimensions.model_dump(),
            "target_word_count": target_word_count,
            "actual_word_count": draft.word_count,
        }

        return {
            "draft": draft,
            "quality_score": last_judge_result.score,
            "attempts": attempts,
            "passed": last_judge_result.passed,
            "generation_metadata": metadata,
        }
```

- [ ] **Step 2: Run pipeline tests — should PASS**

Run: `cd backend && python -m pytest tests/test_agents/test_pipeline.py -v`
Expected: 4 passed

- [ ] **Step 3: Run ALL tests to verify nothing broke**

Run: `cd backend && python -m pytest -v`
Expected: All pass (previous 59 + new ~15 = ~74 tests)

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/article_service.py
git commit -m "feat(services): add generate_with_pipeline orchestration method"
```

---

### Task 7: Lint + Final Verification

- [ ] **Step 1: Run linter**

Run: `cd backend && python -m ruff check app/ tests/`
Expected: `All checks passed!`

If issues found, run: `cd backend && python -m ruff check --fix app/ tests/`

- [ ] **Step 2: Run full test suite**

Run: `cd backend && python -m pytest -v`
Expected: All tests pass

- [ ] **Step 3: Verify module imports work**

Run: `cd backend && python -c "from app.agents.content_generator import ContentGenerator; from app.agents.content_judge import ContentJudge; print('imports OK')"`
Expected: `imports OK`

- [ ] **Step 4: Final commit if any lint fixes were needed, then update phase doc**

Update `docs/phases/phase-1b-llm-generation-pipeline.md` progress section and task statuses (1b.3, 1b.4, 1b.5 → ✅).

- [ ] **Step 5: Merge to develop**

```bash
git checkout develop
git merge --no-ff feature/P1b-2-generation-pipeline -m "merge: Checkpoint 1b-2 complete — ContentGenerator, ContentJudge, pipeline orchestration"
```
