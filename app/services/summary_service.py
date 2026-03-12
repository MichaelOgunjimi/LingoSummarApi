import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.models.summary import Summary


async def create_summary(
    db: AsyncSession,
    *,
    content: str,
    percentage: int,
    text_id: uuid.UUID,
) -> Summary:
    words = len(content.split())
    summary = Summary(
        content=content,
        percentage=percentage,
        words=words,
        text_id=text_id,
    )
    db.add(summary)
    await db.commit()
    await db.refresh(summary)
    return summary


async def get_summaries_by_text_id(
    db: AsyncSession, text_id: uuid.UUID
) -> list[Summary]:
    result = await db.execute(
        select(Summary)
        .where(Summary.text_id == text_id)
        .order_by(col(Summary.created_at).desc())
    )
    return list(result.scalars().all())
