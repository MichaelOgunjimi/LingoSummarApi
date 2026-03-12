# LingoSummar API

FastAPI backend for LingoSummar — a text summarization service powered by a custom NLP pipeline using fuzzy logic, K-means clustering, and TF-IDF feature extraction.

**Live API:** https://lingosummar-api.fastapicloud.dev/api/v1

---

## Tech Stack

- **Framework:** FastAPI (Python 3.12+)
- **Database:** PostgreSQL (Neon serverless) via asyncpg
- **ORM:** SQLModel (SQLAlchemy + Pydantic)
- **Migrations:** Alembic
- **NLP:** spaCy, scikit-learn, custom fuzzy logic engine
- **File Parsing:** PyMuPDF (PDF), python-docx (DOCX)
- **Deployment:** FastAPI Cloud / Docker

---

## API Endpoints

All endpoints are prefixed with `/api/v1`.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/summarize` | Summarize raw text |
| `POST` | `/upload` | Upload and summarize a file (TXT, PDF, DOCX) |
| `POST` | `/summarize-again/{text_id}` | Re-summarize with a different compression % |
| `GET` | `/texts/user` | Get the current user's saved texts (`X-User-UID` header required) |
| `GET` | `/text/summary/{text_id}` | Get a text and all its summaries |

---

## NLP Pipeline

Summarization runs through 5 stages:

1. **Preprocessing** — spaCy tokenization, lemmatization, title extraction
2. **Feature Extraction** — 8 sentence-level features (TF-IDF, position, cue phrases, entity density, bonus/stigma words, length, clustering score)
3. **Clustering** — K-means on sentence word vectors (cosine similarity)
4. **Fuzzy Logic** — 13 inference rules with membership functions → ranked sentences
5. **Selection** — Top-ranked sentences returned in original document order

---

## Project Structure

```
app/
├── main.py              # App factory, CORS, lifespan
├── config.py            # Pydantic settings
├── database.py          # Async engine and session factory
├── api/
│   ├── router.py        # v1 router
│   ├── deps.py          # DB session and auth dependencies
│   └── endpoints/
│       ├── health.py
│       ├── summarize.py
│       └── texts.py
├── models/              # SQLModel DB entities (Text, Summary)
├── schemas/             # Pydantic response schemas
├── services/            # Business logic (text_service, summary_service)
├── summarizer/          # NLP pipeline (engine, preprocessing, features, clustering, fuzzy)
└── utils/
    └── file_handler.py  # TXT / PDF / DOCX extraction
alembic/                 # DB migrations
tests/                   # pytest test suite
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- PostgreSQL database (or a [Neon](https://neon.tech) connection string)

### 1. Clone and install

```bash
git clone https://github.com/MichaelOgunjimi/LingoSummarApi.git
cd LingoSummarApi
uv sync
```

Or with pip:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
APP_NAME=LingoSummar
DEBUG=true
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql+asyncpg://user:password@host/dbname?ssl=require
CORS_ORIGINS=["http://localhost:3000"]
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE_MB=10
DEFAULT_PERCENTAGE=50
```

### 3. Run migrations

```bash
alembic upgrade head
```

### 4. Start the dev server

```bash
uvicorn app.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

---

## Docker

```bash
docker-compose up --build
```

This starts the API on port `8000` with a local PostgreSQL 16 instance.

---

## Running Tests

```bash
pytest
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | `LingoSummar` |
| `DEBUG` | Enable debug mode | `false` |
| `SECRET_KEY` | App secret key | — |
| `DATABASE_URL` | PostgreSQL async connection string | — |
| `CORS_ORIGINS` | JSON array of allowed origins | `[]` |
| `UPLOAD_DIR` | Directory for uploaded files | `./uploads` |
| `MAX_UPLOAD_SIZE_MB` | Max file upload size | `10` |
| `DEFAULT_PERCENTAGE` | Default summary compression % | `50` |
| `NUM_THREADS` | Worker threads for NLP | `8` |

---

## License

MIT
