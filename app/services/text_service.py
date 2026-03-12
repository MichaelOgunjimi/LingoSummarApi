import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select
from sqlalchemy.orm import selectinload

from app.models.text import Text
from app.schemas.text import TextPreview


async def create_text(
    db: AsyncSession,
    *,
    content: str,
    percentage: int,
    user_uid: str | None = None,
    uploaded_filename: str | None = None,
) -> Text:
    text = Text(
        content=content,
        percentage=percentage,
        user_uid=user_uid,
        uploaded_filename=uploaded_filename,
    )
    db.add(text)
    await db.commit()
    await db.refresh(text)
    return text


async def get_all_texts(db: AsyncSession) -> list[TextPreview]:
    result = await db.execute(select(Text).order_by(col(Text.created_at).desc()))
    texts = result.scalars().all()
    return [
        TextPreview(
            id=t.id,
            content_preview=t.content[:200] + "..." if len(t.content) > 200 else t.content,
            user_uid=t.user_uid,
            uploaded_filename=t.uploaded_filename,
            percentage=t.percentage,
            created_at=t.created_at,
        )
        for t in texts
    ]


async def get_texts_by_user(db: AsyncSession, user_uid: str) -> list[TextPreview]:
    result = await db.execute(
        select(Text).where(Text.user_uid == user_uid).order_by(col(Text.created_at).desc())
    )
    texts = result.scalars().all()
    return [
        TextPreview(
            id=t.id,
            content_preview=t.content[:200] + "..." if len(t.content) > 200 else t.content,
            user_uid=t.user_uid,
            uploaded_filename=t.uploaded_filename,
            percentage=t.percentage,
            created_at=t.created_at,
        )
        for t in texts
    ]


async def get_text_by_id(db: AsyncSession, text_id: uuid.UUID) -> Text | None:
    result = await db.execute(select(Text).where(Text.id == text_id))
    return result.scalars().first()


async def get_text_with_summaries(db: AsyncSession, text_id: uuid.UUID) -> Text | None:
    result = await db.execute(
        select(Text)
        .where(Text.id == text_id)
        .options(selectinload(Text.summaries))  # type: ignore[arg-type]
    )
    return result.scalars().first()


async def get_all_texts_with_summaries(db: AsyncSession) -> list[Text]:
    result = await db.execute(
        select(Text)
        .options(selectinload(Text.summaries))  # type: ignore[arg-type]
        .order_by(col(Text.created_at).desc())
    )
    return list(result.scalars().all())
