import uuid
from datetime import datetime

from pydantic import BaseModel


class SummaryResponse(BaseModel):
    """Summary returned from the API."""
    id: uuid.UUID
    content: str
    percentage: int
    words: int
    text_id: uuid.UUID
    created_at: datetime
