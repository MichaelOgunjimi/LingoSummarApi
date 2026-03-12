from fastapi import APIRouter

from app.api.endpoints import health, texts, summarize

# ── v1 API router ────────────────────────────────────────
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router, tags=["health"])
api_router.include_router(texts.router, tags=["texts"])
api_router.include_router(summarize.router, tags=["summarize"])
