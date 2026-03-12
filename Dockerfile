# ── Stage 1: Build ────────────────────────────────────────
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Tell uv to create the venv at /app/.venv (matches runtime path)
ENV UV_PROJECT_ENVIRONMENT="/app/.venv"

# Install deps first (layer cache)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Copy source & install project
COPY . .
RUN uv sync --frozen --no-dev

# Download spaCy model (uv pip instead of spacy download, which requires pip)
RUN uv pip install en-core-web-sm@https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl

# ── Stage 2: Runtime ──────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Copy venv and source from builder (paths already match)
COPY --from=builder /app /app

# Put venv on PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/app/.venv"

# Create uploads dir
RUN mkdir -p /app/uploads

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
