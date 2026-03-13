import json

from pydantic import computed_field
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
    # Accepts a JSON array OR comma-separated string:
    #   CORS_ORIGINS=["https://example.com","http://localhost:3000"]
    #   CORS_ORIGINS=https://example.com,http://localhost:3000
    CORS_ORIGINS: str = (
        "https://lingosummar.michaelogunjimi.com,"
        "https://lingosummar.netlify.app,"
        "http://localhost:3000,"
        "http://localhost:5173"
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origins(self) -> list[str]:
        v = self.CORS_ORIGINS.strip()
        if v.startswith("["):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                pass
        return [origin.strip() for origin in v.split(",") if origin.strip()]

    # ── File uploads ──────────────────────────────────────
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # ── Summarizer defaults ───────────────────────────────
    DEFAULT_PERCENTAGE: int = 50
    NUM_THREADS: int = 8


# Single instance — import this everywhere
settings = Settings()
