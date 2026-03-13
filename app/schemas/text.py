import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.summary import SummaryResponse


# ── Requests ──────────────────────────────────────────────

class SummarizeRequest(BaseModel):
    """POST /summarize body."""
    text: str = Field(min_length=1, max_length=50_000)
    percentage: int | None = Field(default=None, ge=1, le=100)


class SummarizeAgainRequest(BaseModel):
    """POST /summarize-again/{text_id} body."""
    percentage: int | None = Field(default=None, ge=1, le=100)


# ── Responses ─────────────────────────────────────────────

class TextPreview(BaseModel):
    """Lightweight text listing — no full content."""
    id: uuid.UUID
    content_preview: str
    user_uid: str | None
    uploaded_filename: str | None
    percentage: int
    created_at: datetime


class TextResponse(BaseModel):
    """Full text detail."""
    id: uuid.UUID
    content: str
    user_uid: str | None
    uploaded_filename: str | None
    percentage: int
    created_at: datetime


class TextWithSummaries(TextResponse):
    """Text with all its summaries."""
    summaries: list[SummaryResponse] = []
