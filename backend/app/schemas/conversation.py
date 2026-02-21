import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.chat import SourceCitation


class ConversationSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    message_count: int
    updated_at: datetime


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: str
    content: str
    sources: list[SourceCitation] | None = None
    created_at: datetime


class ConversationDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    messages: list[MessageResponse]
