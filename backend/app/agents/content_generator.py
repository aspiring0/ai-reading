"""
ContentGenerator Agent — 生成英语学习文章。

职责：
    根据主题、难度、目标字数生成结构化的英语阅读文章，
    支持自定义指令和基于反馈的重新生成。
"""

from pydantic import BaseModel

from app.agents.base import BaseAgent


class GeneratedSegment(BaseModel):
    """文章的一个段落/标题片段。"""

    segment_index: int
    segment_type: str  # "heading" | "paragraph"
    content: str


class GenerationResult(BaseModel):
    """LLM 生成的文章完整结果。"""

    title: str
    segments: list[GeneratedSegment]
    word_count: int
    cefr_level: str
    difficulty: str


class ContentGenerator(BaseAgent):
    """英语学习文章生成 Agent。

    调用 generate() 方法传入主题和难度，返回 GenerationResult。
    """

    system_prompt = (
        "You are an expert English learning content writer. "
        "Your task is to generate engaging reading articles for English learners.\n\n"
        "Rules:\n"
        "- Difficulty levels: Easy (CEFR A1-A2), Medium (CEFR B1-B2), Hard (CEFR C1-C2)\n"
        "- Structure the article with headings and paragraphs\n"
        "- Match the requested target word count as closely as possible\n"
        "- Use factual, informative content suitable for language learners\n"
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
        """生成一篇英语学习文章。

        Args:
            topic: 文章主题
            difficulty: 难度等级 (easy / medium / hard)
            target_word_count: 目标字数
            custom_instructions: 可选的自定义指令
            previous_feedback: 可选的上一版反馈（用于重新生成）

        Returns:
            GenerationResult 包含标题、分段、字数、CEFR 等级和难度
        """
        user_prompt = (
            f"Topic: {topic}\n"
            f"Difficulty: {difficulty}\n"
            f"Target word count: {target_word_count}"
        )

        if custom_instructions:
            user_prompt += f"\nAdditional instructions: {custom_instructions}"

        if previous_feedback:
            user_prompt += (
                f"\n\nThe previous version had these issues: {previous_feedback}\n"
                "Please address these issues in the new version."
            )

        return await self.call_llm_json(
            user_prompt=user_prompt,
            result_type=GenerationResult,
        )
