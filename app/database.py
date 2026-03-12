from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlmodel import SQLModel

from app.config import settings

# ── Async engine (works with Neon serverless + asyncpg) ──
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    connect_args={
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0,
    },
)

# ── Session factory ──────────────────────────────────────
async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Create all tables. Only used for local dev — use Alembic in production."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a DB session per request."""
    async with async_session() as session:
        yield session
