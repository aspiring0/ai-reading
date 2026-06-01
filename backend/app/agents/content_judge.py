"""
ContentJudge Agent — 评估生成的英语学习文章质量。

职责：
    对 ContentGenerator 生成的文章进行多维度质量评估，
    返回评分、各维度得分和改进反馈。
"""

from pydantic import BaseModel

from app.agents.base import BaseAgent
from app.agents.content_generator import GenerationResult


class JudgeDimensions(BaseModel):
    """评估的四个维度得分。"""

    grammar: float
    vocabulary: float
    coherence: float
    engagement: float


class JudgeResult(BaseModel):
    """内容评估结果。"""

    score: float
    dimensions: JudgeDimensions
    passed: bool
    feedback: str


class ContentJudge(BaseAgent):
    """英语学习内容质量评估 Agent。

    对生成的文章进行 grammar、vocabulary、coherence、engagement
    四个维度的评估，每个维度 0.0-1.0，综合得分为平均值。
    低于 0.7 阈值则不通过，需提供改进反馈。
    """

    system_prompt = (
        "You are an expert English education materials evaluator. "
        "Your task is to evaluate reading articles for English learners "
        "on four dimensions: grammar, vocabulary, coherence, and engagement.\n\n"
        "Evaluation rules:\n"
        "- Each dimension is scored from 0.0 to 1.0\n"
        "- Overall score = average of the four dimensions\n"
        "- Articles with an overall score >= 0.7 pass\n"
        "- Articles below 0.7 fail — provide specific feedback for improvement\n"
        "- Always respond with valid JSON matching the expected schema"
    )

    async def judge(self, draft: GenerationResult) -> JudgeResult:
        """评估一篇生成的文章。

        Args:
            draft: ContentGenerator 生成的文章结果

        Returns:
            JudgeResult 包含评分、维度得分、是否通过和反馈
        """
        full_text = "\n\n".join(seg.content for seg in draft.segments)

        user_prompt = (
            f"Title: {draft.title}\n"
            f"Difficulty: {draft.difficulty}\n"
            f"CEFR Level: {draft.cefr_level}\n"
            f"Word Count: {draft.word_count}\n\n"
            f"Article Content:\n{full_text}"
        )

        return await self.call_llm_json(
            user_prompt=user_prompt,
            result_type=JudgeResult,
        )
