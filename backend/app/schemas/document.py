import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    file_type: str
    file_size: int
    status: str
    page_count: int | None = None
    chunk_count: int
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int


class IngestResponse(BaseModel):
    document_id: uuid.UUID
    status: str
    chunk_count: int
