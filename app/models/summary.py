import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.text import Text


class Summary(SQLModel, table=True):
    """A generated summary belonging to a Text."""

    __tablename__ = "summaries"  # type: ignore[assignment]

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    content: str
    percentage: int = Field(ge=30, le=80)
    words: int = Field(default=0)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    # ── Foreign key ───────────────────────────────────────
    text_id: uuid.UUID = Field(foreign_key="texts.id", index=True)

    # ── Relationship ──────────────────────────────────────
    text: "Text" = Relationship(back_populates="summaries")
