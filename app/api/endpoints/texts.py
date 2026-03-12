import uuid

from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep, RequiredUserUIDDep
from app.schemas.text import TextPreview, TextWithSummaries
from app.services import text_service

router = APIRouter()


@router.get("/texts", response_model=list[TextPreview])
async def list_texts(db: SessionDep):
    """Get all texts (preview only — no full content)."""
    return await text_service.get_all_texts(db)


@router.get("/texts/user", response_model=list[TextPreview])
async def list_user_texts(db: SessionDep, user_uid: RequiredUserUIDDep):
    """Get texts belonging to a specific user (requires X-User-UID header)."""
    return await text_service.get_texts_by_user(db, user_uid)


@router.get("/text/summary/{text_id}", response_model=TextWithSummaries)
async def get_text_with_summaries(text_id: uuid.UUID, db: SessionDep):
    """Get a specific text with all its summaries."""
    text = await text_service.get_text_with_summaries(db, text_id)
    if not text:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Text not found")
    return text


@router.get("/texts-summaries", response_model=list[TextWithSummaries])
async def list_all_texts_with_summaries(db: SessionDep):
    """Get all texts with all their summaries."""
    return await text_service.get_all_texts_with_summaries(db)


@router.get("/texts/{text_id}/summaries", response_model=TextWithSummaries)
async def get_text_summaries_by_id(text_id: uuid.UUID, db: SessionDep):
    """Get a text and its summaries by text ID."""
    text = await text_service.get_text_with_summaries(db, text_id)
    if not text:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Text not found")
    return text
