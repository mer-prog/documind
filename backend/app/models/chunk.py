import uuid
from typing import TYPE_CHECKING, Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.document import Document


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), index=True
    )
    content: Mapped[str] = mapped_column(Text)
    token_count: Mapped[int] = mapped_column(default=0)
    page_number: Mapped[Optional[int]] = mapped_column(nullable=True)
    heading: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    chunk_index: Mapped[int] = mapped_column(default=0)
    embedding = mapped_column(Vector(1536), nullable=True)

    document: Mapped["Document"] = relationship(back_populates="chunks")

    __table_args__ = (
        Index(
            "idx_chunk_content_trgm",
            "content",
            postgresql_using="gin",
            postgresql_ops={"content": "gin_trgm_ops"},
        ),
    )
