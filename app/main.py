import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    # Startup: ensure uploads directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    print(f"🚀 {settings.APP_NAME} is starting up...")
    yield
    # Shutdown
    print(f"👋 {settings.APP_NAME} is shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Intelligent text summarization API powered by NLP and fuzzy logic",
    version="2.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────
app.include_router(api_router)
