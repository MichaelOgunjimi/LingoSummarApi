import json

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    App configuration loaded from environment variables.
    Create a .env file based on .env.example to get started.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Core ──────────────────────────────────────────────
    APP_NAME: str = "LingoSummar"
    DEBUG: bool = False
    SECRET_KEY: str = ...  # type: ignore[assignment]

    # ── Database (Neon serverless PostgreSQL) ─────────────
    DATABASE_URL: str = ...  # type: ignore[assignment]

    # ── CORS ──────────────────────────────────────────────
    CORS_ORIGINS: list[str] = [
        "https://lingosummar.michaelogunjimi.com",
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: object) -> list[str]:
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                return json.loads(v)
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return list(v)  # type: ignore[arg-type]

    # ── File uploads ──────────────────────────────────────
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # ── Summarizer defaults ───────────────────────────────
    DEFAULT_PERCENTAGE: int = 50
    NUM_THREADS: int = 8


# Single instance — import this everywhere
settings = Settings()
