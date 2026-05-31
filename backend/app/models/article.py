"""
文章数据模型。

Article = 一篇英语文章（AI 生成或人工精选）
ArticleSegment = 文章的一个段落/标题（用于分段式阅读）
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Article(Base):
    """文章表 — 存储所有文章的元数据和全文。"""

    __tablename__ = "articles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # ai_generated / curated / user_submitted
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)  # easy / medium / hard
    topic: Mapped[str | None] = mapped_column(String(100))
    word_count: Mapped[int | None] = mapped_column(Integer)
    cefr_level: Mapped[str | None] = mapped_column(String(4))  # A1-C2
    quality_score: Mapped[float | None] = mapped_column(Float)  # 0-1, Judge Agent 评分
    source_url: Mapped[str | None] = mapped_column(Text)
    generation_metadata: Mapped[dict | None] = mapped_column(JSONB)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关系：一篇文章有多个段落
    segments: Mapped[list["ArticleSegment"]] = relationship(
        back_populates="article", cascade="all, delete-orphan", order_by="ArticleSegment.segment_index"
    )

    def __repr__(self) -> str:
        return f"<Article {self.title!r}>"


class ArticleSegment(Base):
    """文章段落表 — 每篇文章拆分成多个段落，用于分段式阅读。"""

    __tablename__ = "article_segments"
    __table_args__ = (UniqueConstraint("article_id", "segment_index", name="uq_article_segment_index"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"))
    segment_index: Mapped[int] = mapped_column(Integer, nullable=False)  # 段落顺序
    segment_type: Mapped[str] = mapped_column(String(20), nullable=False)  # paragraph / heading
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # 关系：段落属于哪篇文章
    article: Mapped["Article"] = relationship(back_populates="segments")

    def __repr__(self) -> str:
        return f"<ArticleSegment {self.article_id}:{self.segment_index}>"
