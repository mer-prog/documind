import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.chunk import Chunk
    from app.models.workspace import Workspace


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id"), nullable=False
    )
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(512))
    file_type: Mapped[str] = mapped_column(String(20))
    file_size: Mapped[int] = mapped_column(default=0)
    file_content: Mapped[Optional[bytes]] = mapped_column(
        LargeBinary, nullable=True, deferred=True
    )
    status: Mapped[str] = mapped_column(String(20), default="pending")
    page_count: Mapped[Optional[int]] = mapped_column(nullable=True)
    chunk_count: Mapped[int] = mapped_column(default=0)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    workspace: Mapped["Workspace"] = relationship(back_populates="documents")
    chunks: Mapped[list["Chunk"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )
