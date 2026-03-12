"""Extract text from uploaded files (TXT, PDF, DOCX)."""

import io

import docx
import fitz  # PyMuPDF
from fastapi import UploadFile

ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx"}


def allowed_file(filename: str) -> bool:
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)


async def read_text_from_upload(file: UploadFile) -> str:
    """Read an uploaded file and return its text content."""
    content = await file.read()
    filename = (file.filename or "").lower()

    if filename.endswith(".txt"):
        return content.decode("utf-8", errors="ignore")

    if filename.endswith(".pdf"):
        return _extract_pdf(content)

    if filename.endswith(".docx"):
        return _extract_docx(content)

    return ""


def _extract_pdf(data: bytes) -> str:
    """Extract text from PDF bytes using PyMuPDF."""
    text_parts: list[str] = []
    with fitz.open(stream=data, filetype="pdf") as doc:
        for page in doc:
            text_parts.append(page.get_text())
    return " ".join(text_parts).replace("\n", " ")


def _extract_docx(data: bytes) -> str:
    """Extract text from DOCX bytes using python-docx."""
    doc = docx.Document(io.BytesIO(data))
    return " ".join(p.text for p in doc.paragraphs if p.text.strip())
