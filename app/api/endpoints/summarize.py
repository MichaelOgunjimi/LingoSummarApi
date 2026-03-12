import uuid
import os

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status

from app.api.deps import SessionDep, UserUIDDep
from app.config import settings
from app.schemas.text import SummarizeRequest, TextWithSummaries
from app.schemas.summary import SummaryResponse
from app.services import text_service, summary_service
from app.summarizer.engine import TextSummarizer
from app.utils.file_handler import read_text_from_upload, allowed_file

router = APIRouter()


DEFAULT_PERCENTAGE = 50


def _get_percentage(value: int | None) -> int:
    """Return provided percentage or the default (50%)."""
    return value if value is not None else DEFAULT_PERCENTAGE


@router.post("/summarize", response_model=TextWithSummaries, status_code=status.HTTP_201_CREATED)
async def summarize_text(body: SummarizeRequest, db: SessionDep, user_uid: UserUIDDep):
    """Submit text for summarization."""
    percentage = _get_percentage(body.percentage)

    # Save the text
    text = await text_service.create_text(
        db, content=body.text, percentage=percentage, user_uid=user_uid,
    )

    # Run summarizer
    summarizer = TextSummarizer(body.text, percentage=percentage, num_threads=settings.NUM_THREADS)
    summary_content = summarizer.summarize()

    # Save the summary
    summary = await summary_service.create_summary(
        db, content=summary_content, percentage=percentage, text_id=text.id,
    )

    # Return the text with its summary
    text_with_summaries = await text_service.get_text_with_summaries(db, text.id)
    return text_with_summaries


@router.post("/upload", response_model=TextWithSummaries, status_code=status.HTTP_201_CREATED)
async def upload_and_summarize(
    db: SessionDep,
    user_uid: UserUIDDep,
    file: UploadFile = File(...),
    percentage: int = Form(default=50),
):
    """Upload a file (TXT, PDF, DOCX) and summarize it."""
    if not file.filename or not allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not allowed. Supported: .txt, .pdf, .docx",
        )

    percentage = _get_percentage(percentage)

    # Extract text from file
    content = await read_text_from_upload(file)
    if not content or not content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract text from the uploaded file",
        )

    # Save text
    text = await text_service.create_text(
        db,
        content=content,
        percentage=percentage,
        user_uid=user_uid,
        uploaded_filename=file.filename,
    )

    # Run summarizer
    summarizer = TextSummarizer(content, percentage=percentage, num_threads=settings.NUM_THREADS)
    summary_content = summarizer.summarize()

    # Save summary
    await summary_service.create_summary(
        db, content=summary_content, percentage=percentage, text_id=text.id,
    )

    text_with_summaries = await text_service.get_text_with_summaries(db, text.id)
    return text_with_summaries


@router.post(
    "/summarize-again/{text_id}",
    response_model=SummaryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def summarize_again(text_id: uuid.UUID, db: SessionDep, percentage: int = 50):
    """Generate a new summary for an existing text at a (possibly different) compression rate."""
    text = await text_service.get_text_by_id(db, text_id)
    if not text:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Text not found")

    percentage = _get_percentage(percentage)

    summarizer = TextSummarizer(text.content, percentage=percentage, num_threads=settings.NUM_THREADS)
    summary_content = summarizer.summarize()

    summary = await summary_service.create_summary(
        db, content=summary_content, percentage=percentage, text_id=text.id,
    )
    return summary
