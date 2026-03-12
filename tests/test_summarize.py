"""Tests for /api/v1/summarize, /upload, and /summarize-again endpoints."""

import uuid
from unittest.mock import patch, MagicMock

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.text import Text


# ── Helpers ───────────────────────────────────────────────

async def _seed_text(
    db: AsyncSession,
    *,
    content: str = "Climate change is one of the most pressing issues today. "
                   "Rising temperatures have led to melting ice caps.",
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


MOCK_SUMMARY = "Climate change is pressing."


def _mock_summarizer():
    """Patch TextSummarizer so tests don't run the real NLP pipeline."""
    mock = MagicMock()
    mock.return_value.summarize.return_value = MOCK_SUMMARY
    return mock


# ── POST /summarize ──────────────────────────────────────

@pytest.mark.asyncio
@patch("app.api.endpoints.summarize.TextSummarizer", new_callable=_mock_summarizer)
async def test_summarize_text(mock_ts, client: AsyncClient):
    response = await client.post(
        "/api/v1/summarize",
        json={"text": "A long piece of text that needs summarization.", "percentage": 50},
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "summaries" in data
    assert len(data["summaries"]) == 1
    assert data["summaries"][0]["content"] == MOCK_SUMMARY


@pytest.mark.asyncio
@patch("app.api.endpoints.summarize.TextSummarizer", new_callable=_mock_summarizer)
async def test_summarize_text_empty_body(mock_ts, client: AsyncClient):
    response = await client.post("/api/v1/summarize", json={"text": "", "percentage": 50})
    assert response.status_code == 422  # validation error: min_length=1


# ── POST /summarize-again/{text_id} ──────────────────────

@pytest.mark.asyncio
@patch("app.api.endpoints.summarize.TextSummarizer", new_callable=_mock_summarizer)
async def test_summarize_again(mock_ts, client: AsyncClient, db_session: AsyncSession):
    text = await _seed_text(db_session)
    response = await client.post(f"/api/v1/summarize-again/{text.id}?percentage=40")
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == MOCK_SUMMARY
    assert data["text_id"] == str(text.id)


@pytest.mark.asyncio
@patch("app.api.endpoints.summarize.TextSummarizer", new_callable=_mock_summarizer)
async def test_summarize_again_not_found(mock_ts, client: AsyncClient):
    fake_id = uuid.uuid4()
    response = await client.post(f"/api/v1/summarize-again/{fake_id}?percentage=50")
    assert response.status_code == 404


# ── POST /upload ──────────────────────────────────────────

@pytest.mark.asyncio
@patch("app.api.endpoints.summarize.TextSummarizer", new_callable=_mock_summarizer)
async def test_upload_txt_file(mock_ts, client: AsyncClient):
    response = await client.post(
        "/api/v1/upload",
        files={"file": ("test.txt", b"Some long text content for summarization.", "text/plain")},
        data={"percentage": "50"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["uploaded_filename"] == "test.txt"
    assert len(data["summaries"]) == 1


@pytest.mark.asyncio
async def test_upload_disallowed_extension(client: AsyncClient):
    response = await client.post(
        "/api/v1/upload",
        files={"file": ("test.exe", b"binary data", "application/octet-stream")},
        data={"percentage": "50"},
    )
    assert response.status_code == 400
    assert "File type not allowed" in response.json()["detail"]


@pytest.mark.asyncio
@patch("app.api.endpoints.summarize.read_text_from_upload", return_value="")
async def test_upload_empty_content(mock_read, client: AsyncClient):
    response = await client.post(
        "/api/v1/upload",
        files={"file": ("test.txt", b"", "text/plain")},
        data={"percentage": "50"},
    )
    assert response.status_code == 400
    assert "Could not extract text" in response.json()["detail"]
