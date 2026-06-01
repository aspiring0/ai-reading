# Content Generation Pipeline Design

> Date: 2026-06-01
> Checkpoint: 1b-2
> Status: Draft

## Overview

Two LLM Agents (ContentGenerator + ContentJudge) orchestrated by Service layer to auto-generate English reading articles with quality control.

## Architecture

```
Service.generate_with_pipeline()
    │
    ├─ attempt 1: Generator → Judge
    │     ├─ passed → store
    │     └─ failed → collect feedback
    │
    ├─ attempt 2: Generator(feedback) → Judge
    │     ├─ passed → store
    │     └─ failed → collect feedback
    │
    └─ attempt 3: Generator(feedback) → Judge
          └─ store regardless (with low quality_score)
```

Max 3 attempts. Store last result even if score < 0.7.

## Component 1: ContentGenerator

**File:** `backend/app/agents/content_generator.py`
**Inherits:** `BaseAgent`

### Input (Pydantic)

```python
class GenerationRequest(BaseModel):
    topic: str                          # "climate change", "AI ethics"
    difficulty: str                     # easy / medium / hard
    target_word_count: int = 300        # 目标字数
    custom_instructions: str | None     # 用户额外要求
    previous_feedback: str | None       # Judge 的改进建议（重试时用）
```

### Output (Pydantic)

```python
class GeneratedSegment(BaseModel):
    segment_index: int
    segment_type: str       # heading / paragraph
    content: str

class GenerationResult(BaseModel):
    title: str
    segments: list[GeneratedSegment]
    word_count: int
    cefr_level: str         # A1-C2
    difficulty: str
```

### Agent Method

```python
async def generate(self, topic, difficulty, target_word_count,
                   custom_instructions=None, previous_feedback=None) -> GenerationResult:
    user_prompt = f"Topic: {topic}\nDifficulty: {difficulty}\nTarget words: {target_word_count}"
    if custom_instructions:
        user_prompt += f"\nAdditional instructions: {custom_instructions}"
    if previous_feedback:
        user_prompt += f"\n\nThe previous version had these issues:\n{previous_feedback}\nPlease address them."
    return await self.call_llm_json(user_prompt, result_type=GenerationResult)
```

### System Prompt (English)

```
You are an expert English learning content writer. Generate engaging
reading materials for English learners.

Rules:
- Match the requested difficulty level in vocabulary and sentence complexity
- Easy: simple sentences, common words (CEFR A1-A2)
- Medium: varied sentences, some academic vocabulary (CEFR B1-B2)
- Hard: complex sentences, advanced vocabulary (CEFR C1-C2)
- Structure the article with headings and paragraphs
- Target approximately {target_word_count} words
- Content must be factual and educational

{custom_instructions}
{previous_feedback}
```

## Component 2: ContentJudge

**File:** `backend/app/agents/content_judge.py`
**Inherits:** `BaseAgent`

### Agent Method

```python
async def judge(self, draft: GenerationResult) -> JudgeResult:
    # 把 segments 拼成完整文本给 LLM 看（LLM 不需要看结构化 JSON）
    full_text = "\n\n".join(seg.content for seg in draft.segments)
    user_prompt = f"""Evaluate this English learning article:
Title: {draft.title}
Difficulty: {draft.difficulty}
Target word count: {draft.word_count}

Article content:
{full_text}"""
    return await self.call_llm_json(user_prompt, result_type=JudgeResult)
```

### Input (Pydantic)

```python
class JudgeRequest(BaseModel):
    title: str
    segments: list[GeneratedSegment]
    difficulty: str
    target_word_count: int
```

### Output (Pydantic)

```python
class JudgeDimensions(BaseModel):
    grammar: float          # 0-1, 语法正确性
    vocabulary: float       # 0-1, 词汇多样性和适当性
    coherence: float        # 0-1, 段落间逻辑连贯
    engagement: float       # 0-1, 对学习者的吸引力

class JudgeResult(BaseModel):
    score: float            # 4维平均分
    dimensions: JudgeDimensions
    passed: bool            # score >= 0.7
    feedback: str           # 改进建议（不达标时详细说明问题）
```

### System Prompt (English)

```
You are an expert English education materials evaluator.
Evaluate the given article on 4 dimensions (each 0.0 to 1.0):

1. grammar: Are there grammatical errors? Are tenses used correctly?
2. vocabulary: Is vocabulary diverse and appropriate for the difficulty?
3. coherence: Do paragraphs flow logically? Is the structure clear?
4. engagement: Would a learner find this interesting and motivating?

Overall score = average of 4 dimensions.
Pass threshold: 0.7

If score < 0.7, provide specific, actionable feedback explaining
what to improve. Be constructive, not just critical.
```

## Component 3: Pipeline Orchestration

**File:** `backend/app/services/article_service.py` (extend existing)

### Method

```python
async def generate_with_pipeline(
    self,
    topic: str,
    difficulty: str,
    target_word_count: int = 300,
    custom_instructions: str | None = None,
) -> dict:
    """Run generate→judge pipeline, return article + metadata."""
```

### Pipeline Logic

```python
generator = ContentGenerator()
judge = ContentJudge()
feedback = None
attempts = 0
last_judge_result = None

for attempt in range(3):
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

# Store article with metadata
article = await self.create_article_from_generation(
    draft, last_judge_result.score, attempts
)
return {"article_id": article.id, "quality_score": ..., "attempts": attempts, ...}
```

### generation_metadata Schema

```json
{
    "model": "glm-5",
    "source": "ai_generated",
    "attempts": 2,
    "passed": true,
    "final_score": 0.82,
    "dimensions": {"grammar": 0.9, "vocabulary": 0.8, "coherence": 0.75, "engagement": 0.85},
    "target_word_count": 300,
    "actual_word_count": 310
}
```

## Error Handling

| Scenario | Handling |
|---|---|
| LLM call fails (network/timeout) | LLMClient retries 3x with backoff, then ExternalServiceException |
| LLM returns invalid JSON | BaseAgent retries 2x with error hint, then ExternalServiceException |
| All 3 pipeline attempts score < 0.7 | Store last result with low quality_score, `is_published=false` (草稿状态，需管理员手动发布) |
| Pipeline takes too long | Not handled in this checkpoint (1b-3 adds BackgroundTasks) |

## Testing Strategy

All tests mock LLM responses, no real API calls.

| Test | What to verify |
|---|---|
| ContentGenerator unit | Mock LLM returns valid JSON → GenerationResult parsed correctly |
| ContentGenerator with feedback | previous_feedback injected into prompt |
| ContentJudge unit | Mock LLM returns scores → JudgeResult with passed=true/false |
| Pipeline normal path | Generator → Judge(passed=true) → store once |
| Pipeline retry path | Judge(passed=false) → feedback → Generator again → Judge(passed=true) → store |
| Pipeline max retry | Judge fails 3x → store last result with low score |
| Pipeline metadata | Verify generation_metadata contains correct attempts, score, model |

## Decisions

- **Prompt language:** English (better LLM output quality)
- **Max attempts:** 3 (generator + judge = 1 attempt)
- **Failure policy:** Store last result, mark as low quality
- **Pass threshold:** 0.7 (average of 4 dimensions)
