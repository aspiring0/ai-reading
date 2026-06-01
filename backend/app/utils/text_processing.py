"""
文本处理工具 — 分段、字数统计、阅读时间估算。

纯函数，不依赖数据库和外部服务，方便测试和复用。
"""

import re


def count_words(text: str) -> int:
    """统计英文单词数。按空格分词，忽略多余空白。"""
    return len(text.split())


def estimate_reading_time(word_count: int, wpm: int = 200) -> int:
    """估算阅读时间（分钟）。

    Args:
        word_count: 单词数
        wpm: 每分钟阅读词数，默认 200（中等英语学习者偏慢）

    Returns:
        向上取整的分钟数，最少 1 分钟
    """
    if word_count <= 0:
        return 0
    minutes = word_count / wpm
    return max(1, int(minutes) if minutes == int(minutes) else int(minutes) + 1)


def split_into_paragraphs(text: str) -> list[dict]:
    """将文章全文按空行拆分成段落列表。

    Returns:
        [{"segment_index": 0, "segment_type": "paragraph", "content": "..."}, ...]
    """
    # 按一个或多个空行拆分
    raw_paragraphs = re.split(r"\n\s*\n", text.strip())
    result = []
    for para in raw_paragraphs:
        para = para.strip()
        if not para:
            continue
        # 简单启发式：短行（<60字符）且不以标点结尾的视为标题
        seg_type = "heading" if len(para) < 60 and para[-1] not in ".!?" else "paragraph"
        result.append(
            {
                "segment_index": len(result),
                "segment_type": seg_type,
                "content": para,
            }
        )
    return result
