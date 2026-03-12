"""Tests for /api/v1/texts endpoints."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.text import Text
from app.models.summary import Summary


# ── Helpers ───────────────────────────────────────────────

async def _seed_text(
    db: AsyncSession,
    *,
    content: str = "Climate change is one of the most pressing issues today.",
    percentage: int = 50,
    user_uid: str | None = "test-user-123",
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


async def _seed_summary(
    db: AsyncSession,
    text_id: uuid.UUID,
    *,
    content: str = "Climate change is pressing.",
    percentage: int = 50,
    words: int = 4,
) -> Summary:
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


# ── GET /texts ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_texts_empty(client: AsyncClient):
    response = await client.get("/api/v1/texts")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_texts_returns_previews(client: AsyncClient, db_session: AsyncSession):
    await _seed_text(db_session)
    response = await client.get("/api/v1/texts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert "content_preview" in data[0]
    assert "id" in data[0]


# ── GET /texts/user ───────────────────────────────────────

@pytest.mark.asyncio
async def test_list_user_texts(client: AsyncClient, db_session: AsyncSession):
    await _seed_text(db_session, user_uid="test-user-123")
    await _seed_text(db_session, user_uid="other-user")
    response = await client.get("/api/v1/texts/user")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["user_uid"] == "test-user-123"


@pytest.mark.asyncio
async def test_list_user_texts_requires_auth(client_no_user: AsyncClient):
    response = await client_no_user.get("/api/v1/texts/user")
    assert response.status_code == 401


# ── GET /text/summary/{text_id} ──────────────────────────

@pytest.mark.asyncio
async def test_get_text_with_summaries(client: AsyncClient, db_session: AsyncSession):
    text = await _seed_text(db_session)
    await _seed_summary(db_session, text.id)
    response = await client.get(f"/api/v1/text/summary/{text.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(text.id)
    assert len(data["summaries"]) == 1


@pytest.mark.asyncio
async def test_get_text_with_summaries_not_found(client: AsyncClient):
    import uuid
    fake_id = uuid.uuid4()
    response = await client.get(f"/api/v1/text/summary/{fake_id}")
    assert response.status_code == 404


# ── GET /texts-summaries ─────────────────────────────────

@pytest.mark.asyncio
async def test_list_all_texts_with_summaries(client: AsyncClient, db_session: AsyncSession):
    text = await _seed_text(db_session)
    await _seed_summary(db_session, text.id)
    response = await client.get("/api/v1/texts-summaries")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert len(data[0]["summaries"]) == 1


# ── GET /texts/{text_id}/summaries ────────────────────────

@pytest.mark.asyncio
async def test_get_text_summaries_by_id(client: AsyncClient, db_session: AsyncSession):
    text = await _seed_text(db_session)
    await _seed_summary(db_session, text.id, percentage=40)
    await _seed_summary(db_session, text.id, percentage=60)
    response = await client.get(f"/api/v1/texts/{text.id}/summaries")
    assert response.status_code == 200
    data = response.json()
    assert len(data["summaries"]) == 2


@pytest.mark.asyncio
async def test_get_text_summaries_by_id_not_found(client: AsyncClient):
    import uuid
    fake_id = uuid.uuid4()
    response = await client.get(f"/api/v1/texts/{fake_id}/summaries")
    assert response.status_code == 404
