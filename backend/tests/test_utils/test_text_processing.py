"""
text_processing 工具测试 — 验证字数统计、阅读时间、分段逻辑。
"""

from app.utils.text_processing import count_words, estimate_reading_time, split_into_paragraphs


class TestCountWords:
    def test_normal_sentence(self):
        assert count_words("Hello world this is a test") == 6

    def test_empty_string(self):
        assert count_words("") == 0

    def test_extra_spaces(self):
        assert count_words("  hello   world  ") == 2

    def test_single_word(self):
        assert count_words("Hello") == 1


class TestEstimateReadingTime:
    def test_short_article(self):
        """200 词以下 = 1 分钟。"""
        assert estimate_reading_time(150) == 1

    def test_exact_200_words(self):
        """刚好 200 词 = 1 分钟。"""
        assert estimate_reading_time(200) == 1

    def test_400_words(self):
        """400 词 = 2 分钟。"""
        assert estimate_reading_time(400) == 2

    def test_500_words(self):
        """500 词 = 3 分钟（向上取整）。"""
        assert estimate_reading_time(500) == 3

    def test_zero_words(self):
        assert estimate_reading_time(0) == 0

    def test_custom_wpm(self):
        """自定义阅读速度。"""
        assert estimate_reading_time(300, wpm=150) == 2


class TestSplitIntoParagraphs:
    def test_single_paragraph(self):
        result = split_into_paragraphs("Just one paragraph.")
        assert len(result) == 1
        assert result[0]["segment_type"] == "paragraph"
        assert result[0]["content"] == "Just one paragraph."

    def test_multiple_paragraphs(self):
        text = "First paragraph here.\n\nSecond paragraph here."
        result = split_into_paragraphs(text)
        assert len(result) == 2
        assert result[0]["segment_index"] == 0
        assert result[1]["segment_index"] == 1

    def test_heading_detection(self):
        """短行（<60字符）且不以句号结尾 → 标题。"""
        text = "Chapter 1\n\nThis is the content of chapter one. It has enough text to be a paragraph."
        result = split_into_paragraphs(text)
        assert result[0]["segment_type"] == "heading"
        assert result[1]["segment_type"] == "paragraph"

    def test_empty_input(self):
        result = split_into_paragraphs("")
        assert result == []

    def test_trailing_whitespace(self):
        text = "Hello world.\n\n  "
        result = split_into_paragraphs(text)
        assert len(result) == 1
