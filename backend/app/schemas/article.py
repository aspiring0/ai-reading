"""
文章相关的 Pydantic 模型（请求/响应格式）。

schemas/ 定义 API 层的数据格式，和 models/（数据库格式）分开。
比如响应中不包含 content（全文），列表只需要摘要信息。
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

# --- 嵌套模型 ---


class SegmentBase(BaseModel):
    segment_index: int
    segment_type: str  # paragraph / heading
    content: str


class SegmentResponse(SegmentBase):
    id: uuid.UUID

    model_config = {"from_attributes": True}


# --- 创建 ---


class ArticleCreate(BaseModel):
    """创建文章的请求体（Admin 用）。"""

    title: str = Field(..., max_length=500)
    source: str = Field(..., max_length=50)  # ai_generated / curated / user_submitted
    difficulty: str = Field(..., max_length=20)  # easy / medium / hard
    topic: str | None = Field(None, max_length=100)
    cefr_level: str | None = Field(None, max_length=4)
    content: str
    segments: list[SegmentBase] | None = None  # 可选：传入分段数据


# --- 更新 ---


class ArticleUpdate(BaseModel):
    """更新文章的请求体（Admin 用），所有字段可选。"""

    title: str | None = Field(None, max_length=500)
    difficulty: str | None = Field(None, max_length=20)
    topic: str | None = Field(None, max_length=100)
    cefr_level: str | None = Field(None, max_length=4)
    is_published: bool | None = None
    content: str | None = None


# --- 响应 ---


class ArticleResponse(BaseModel):
    """文章详情响应（包含段落）。"""

    id: uuid.UUID
    title: str
    source: str
    difficulty: str
    topic: str | None
    cefr_level: str | None
    word_count: int | None
    quality_score: float | None
    is_published: bool
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime
    content: str
    segments: list[SegmentResponse] = []
    estimated_reading_time_minutes: int | None = None  # 阅读时间（分钟），由 Service 层计算

    model_config = {"from_attributes": True}


class ArticleListItem(BaseModel):
    """文章列表中的单条（不含全文和段落）。"""

    id: uuid.UUID
    title: str
    difficulty: str
    topic: str | None
    cefr_level: str | None
    word_count: int | None
    is_published: bool
    published_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ArticleListResponse(BaseModel):
    """文章列表响应（带分页）。"""

    items: list[ArticleListItem]
    total: int
    page: int
    page_size: int
    pages: int
