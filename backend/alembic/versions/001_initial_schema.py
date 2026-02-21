"""initial schema

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # Workspaces
    op.create_table(
        "workspaces",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("api_key_hash", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # Users
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="member"),
        sa.Column(
            "workspace_id",
            sa.Uuid(),
            sa.ForeignKey("workspaces.id"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # Documents
    op.create_table(
        "documents",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "workspace_id",
            sa.Uuid(),
            sa.ForeignKey("workspaces.id"),
            nullable=False,
        ),
        sa.Column(
            "uploaded_by", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column("filename", sa.String(512), nullable=False),
        sa.Column("file_type", sa.String(20), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("file_content", sa.LargeBinary(), nullable=True),
        sa.Column(
            "status", sa.String(20), nullable=False, server_default="pending"
        ),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("chunk_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("content_hash", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # Chunks
    op.create_table(
        "chunks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "document_id",
            sa.Uuid(),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("heading", sa.String(512), nullable=True),
        sa.Column("chunk_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("embedding", Vector(1536), nullable=True),
    )
    op.create_index("ix_chunks_document_id", "chunks", ["document_id"])
    op.execute(
        "CREATE INDEX idx_chunk_content_trgm ON chunks "
        "USING gin (content gin_trgm_ops)"
    )

    # Conversations
    op.create_table(
        "conversations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column(
            "workspace_id",
            sa.Uuid(),
            sa.ForeignKey("workspaces.id"),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(512),
            nullable=False,
            server_default="New Conversation",
        ),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column(
            "message_count", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_conversations_user_id", "conversations", ["user_id"])

    # Messages
    op.create_table(
        "messages",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "conversation_id",
            sa.Uuid(),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sources", sa.JSON(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])

    # Daily Analytics
    op.create_table(
        "daily_analytics",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "workspace_id",
            sa.Uuid(),
            sa.ForeignKey("workspaces.id"),
            nullable=False,
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column(
            "total_queries", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "total_tokens_prompt", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "total_tokens_completion",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "average_latency_ms",
            sa.Float(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("query_texts", sa.JSON(), nullable=True),
        sa.UniqueConstraint(
            "workspace_id", "date", name="uq_analytics_workspace_date"
        ),
    )
    op.create_index("ix_daily_analytics_date", "daily_analytics", ["date"])


def downgrade() -> None:
    op.drop_table("daily_analytics")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_index("idx_chunk_content_trgm", table_name="chunks")
    op.drop_table("chunks")
    op.drop_table("documents")
    op.drop_table("users")
    op.drop_table("workspaces")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
    op.execute("DROP EXTENSION IF EXISTS vector")
