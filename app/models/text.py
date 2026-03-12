import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.summary import Summary


class Text(SQLModel, table=True):
    """A piece of text submitted for summarization."""

    __tablename__ = "texts" # type:ignore[assignment]

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    content: str
    user_uid: str | None = Field(default=None, index=True)
    uploaded_filename: str | None = None
    percentage: int = Field(default=50, ge=30, le=80)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    # ── Relationship ──────────────────────────────────────
    summaries: list["Summary"] = Relationship(back_populates="text")
