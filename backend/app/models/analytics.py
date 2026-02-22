import datetime
import uuid
from typing import Optional

from sqlalchemy import JSON, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class DailyAnalytics(Base):
    __tablename__ = "daily_analytics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id"), nullable=False
    )
    date: Mapped[datetime.date] = mapped_column(Date, index=True)
    total_queries: Mapped[int] = mapped_column(default=0)
    total_tokens_prompt: Mapped[int] = mapped_column(default=0)
    total_tokens_completion: Mapped[int] = mapped_column(default=0)
    average_latency_ms: Mapped[float] = mapped_column(default=0.0)
    query_texts: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        UniqueConstraint("workspace_id", "date", name="uq_analytics_workspace_date"),
    )
