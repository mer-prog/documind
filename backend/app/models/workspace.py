import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.user import User


class Workspace(Base, TimestampMixin):
    __tablename__ = "workspaces"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    api_key_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    members: Mapped[list["User"]] = relationship(back_populates="workspace")
    documents: Mapped[list["Document"]] = relationship(back_populates="workspace")
