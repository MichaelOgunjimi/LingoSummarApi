"""Shared fixtures for endpoint tests.

Uses an in-memory SQLite database so tests never touch a real DB.
"""

import pytest
import pytest_asyncio
from collections.abc import AsyncGenerator
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel

from app.main import app
from app.api.deps import get_user_uid, require_user_uid
from app.database import get_session

# ── Import models so SQLModel.metadata knows about them ──
from app.models.text import Text  # noqa: F401
from app.models.summary import Summary  # noqa: F401

# ── In-memory SQLite engine for tests ────────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite://"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)


# ── Create / drop tables per test ────────────────────────
@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


# ── Session override ─────────────────────────────────────
@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client with DB session override."""

    async def _override_get_session():
        yield db_session

    async def _override_user_uid():
        return "test-user-123"

    async def _override_require_user_uid():
        return "test-user-123"

    app.dependency_overrides[get_session] = _override_get_session
    app.dependency_overrides[get_user_uid] = _override_user_uid
    app.dependency_overrides[require_user_uid] = _override_require_user_uid

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client_no_user(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Client without user UID override — for testing auth-required routes."""

    async def _override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = _override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
