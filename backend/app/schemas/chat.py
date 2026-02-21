import uuid

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    conversation_id: uuid.UUID | None = None


class SourceCitation(BaseModel):
    chunk_id: uuid.UUID
    document_name: str
    page_number: int | None = None
    text_snippet: str
    relevance_score: float


class ChatChunkEvent(BaseModel):
    type: str  # "token", "sources", "done", "error"
    content: str | None = None
    sources: list[SourceCitation] | None = None
    conversation_id: uuid.UUID | None = None
