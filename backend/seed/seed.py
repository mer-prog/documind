"""
Seed script for DocuMind.

Run from the backend directory:
    python -m seed.seed              # Uses mock embeddings (no API key needed)
    python -m seed.seed --use-openai # Uses real OpenAI embeddings

Requires:
    - DATABASE_URL set in .env or environment
    - Database with migrations applied (alembic upgrade head)
"""

import argparse
import asyncio
import json
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import bcrypt
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.models import Base, Chunk, Conversation, DailyAnalytics, Document, Message, User, Workspace
from app.services import embedding_service
from app.services.ingest_service import chunk_text, count_tokens, parse_markdown

SEED_DATA_DIR = Path(__file__).parent / "data"

SEED_DOCUMENTS = [
    "company-handbook.md",
    "product-roadmap.md",
    "api-documentation.md",
]

ADMIN_EMAIL = "admin@documind.dev"
ADMIN_PASSWORD = "password123"
ADMIN_NAME = "Admin User"
WORKSPACE_NAME = "Acme Corp Knowledge Base"


def parse_args():
    parser = argparse.ArgumentParser(description="Seed DocuMind database")
    parser.add_argument(
        "--use-openai",
        action="store_true",
        default=False,
        help="Use real OpenAI API for embeddings instead of mock embeddings",
    )
    return parser.parse_args()


async def main():
    args = parse_args()
    use_openai = args.use_openai

    if use_openai and not settings.OPENAI_API_KEY:
        print("ERROR: --use-openai flag requires OPENAI_API_KEY to be set")
        sys.exit(1)

    mode = "OpenAI API" if use_openai else "mock embeddings"
    print(f"Starting DocuMind seed ({mode})...")
    print(f"Database: {settings.DATABASE_URL[:50]}...")

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_factory() as db:
        # Create workspace
        workspace_id = uuid.uuid4()
        workspace = Workspace(
            id=workspace_id,
            name=WORKSPACE_NAME,
        )
        db.add(workspace)
        await db.flush()
        print(f"Created workspace: {WORKSPACE_NAME} ({workspace_id})")

        # Create admin user
        hashed_pw = bcrypt.hashpw(
            ADMIN_PASSWORD.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            email=ADMIN_EMAIL,
            hashed_password=hashed_pw,
            name=ADMIN_NAME,
            role="admin",
            workspace_id=workspace_id,
        )
        db.add(user)
        await db.flush()
        print(f"Created admin user: {ADMIN_EMAIL} ({user_id})")

        total_chunks = 0
        total_tokens = 0
        first_doc_chunks = []  # Keep references for sample conversations

        for filename in SEED_DOCUMENTS:
            filepath = SEED_DATA_DIR / filename
            print(f"\nProcessing: {filename}")

            content = filepath.read_text(encoding="utf-8")
            file_bytes = content.encode("utf-8")

            # Create document
            doc_id = uuid.uuid4()
            document = Document(
                id=doc_id,
                workspace_id=workspace_id,
                uploaded_by=user_id,
                filename=filename,
                file_type="md",
                file_size=len(file_bytes),
                status="completed",
            )
            db.add(document)
            await db.flush()

            # Parse and chunk
            raw_chunks = parse_markdown(content)
            processed_chunks = chunk_text(raw_chunks)
            print(f"  Chunks: {len(processed_chunks)}")

            # Generate embeddings
            texts = [c.content for c in processed_chunks]
            print(f"  Generating embeddings for {len(texts)} chunks...")

            if use_openai:
                from openai import AsyncOpenAI

                openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                all_embeddings = []
                batch_size = 100
                for i in range(0, len(texts), batch_size):
                    batch = texts[i : i + batch_size]
                    response = await openai_client.embeddings.create(
                        model=settings.EMBEDDING_MODEL,
                        input=batch,
                    )
                    all_embeddings.extend([item.embedding for item in response.data])
            else:
                all_embeddings = [
                    embedding_service.generate_mock_embedding(t, settings.EMBEDDING_DIMENSIONS)
                    for t in texts
                ]

            # Create chunk records
            chunk_ids = []
            for i, (pc, emb) in enumerate(zip(processed_chunks, all_embeddings)):
                chunk_id = uuid.uuid4()
                chunk = Chunk(
                    id=chunk_id,
                    document_id=doc_id,
                    workspace_id=workspace_id,
                    content=pc.content,
                    token_count=pc.token_count,
                    page_number=pc.page_number,
                    heading=pc.heading,
                    chunk_index=pc.chunk_index,
                    embedding=emb,
                )
                db.add(chunk)
                chunk_ids.append(chunk_id)
                if filename == "company-handbook.md" and len(first_doc_chunks) < 3:
                    first_doc_chunks.append({
                        "chunk_id": str(chunk_id),
                        "document_name": filename,
                        "page_number": pc.page_number,
                        "heading": pc.heading,
                        "text_snippet": pc.content[:300],
                        "relevance_score": 0.032,
                    })

            document.chunk_count = len(processed_chunks)
            total_chunks += len(processed_chunks)
            total_tokens += sum(c.token_count for c in processed_chunks)

            await db.flush()
            print(f"  Done: {len(processed_chunks)} chunks, {sum(c.token_count for c in processed_chunks)} tokens")

        # ── Sample Conversations ──
        print("\nCreating sample conversations...")

        # Conversation 1
        conv1_id = uuid.uuid4()
        conv1 = Conversation(
            id=conv1_id,
            user_id=user_id,
            workspace_id=workspace_id,
            title="Remote work policy question",
            message_count=2,
        )
        db.add(conv1)
        await db.flush()

        db.add(Message(
            id=uuid.uuid4(),
            conversation_id=conv1_id,
            role="user",
            content="What is the remote work policy?",
            token_count=7,
            created_at=datetime.utcnow() - timedelta(hours=2),
        ))
        db.add(Message(
            id=uuid.uuid4(),
            conversation_id=conv1_id,
            role="assistant",
            content=(
                "Based on the company handbook, the remote work policy allows team members to work "
                "from home up to 3 days per week. Core collaboration hours are 10 AM to 3 PM in your "
                "local timezone. You need manager approval for fully remote arrangements.\n\n"
                "[Source: company-handbook.md]"
            ),
            token_count=48,
            sources=first_doc_chunks[:2] if first_doc_chunks else None,
            latency_ms=1250,
            created_at=datetime.utcnow() - timedelta(hours=2, minutes=-1),
        ))

        # Conversation 2
        conv2_id = uuid.uuid4()
        conv2 = Conversation(
            id=conv2_id,
            user_id=user_id,
            workspace_id=workspace_id,
            title="Q1 product roadmap milestones",
            message_count=2,
        )
        db.add(conv2)
        await db.flush()

        db.add(Message(
            id=uuid.uuid4(),
            conversation_id=conv2_id,
            role="user",
            content="What are the key milestones for Q1?",
            token_count=9,
            created_at=datetime.utcnow() - timedelta(hours=1),
        ))
        db.add(Message(
            id=uuid.uuid4(),
            conversation_id=conv2_id,
            role="assistant",
            content=(
                "According to the product roadmap, the Q1 milestones include:\n\n"
                "1. **Core Platform Launch** — Release the initial document ingestion pipeline "
                "with support for PDF, DOCX, and Markdown formats.\n"
                "2. **Semantic Search MVP** — Deploy hybrid search combining vector similarity "
                "and keyword matching with RRF fusion.\n"
                "3. **Analytics Dashboard** — Ship usage tracking with token consumption and "
                "query performance metrics.\n\n"
                "[Source: product-roadmap.md]"
            ),
            token_count=85,
            sources=None,
            latency_ms=980,
            created_at=datetime.utcnow() - timedelta(hours=1, minutes=-1),
        ))
        print("  Created 2 sample conversations with messages")

        await db.commit()

        # Create IVFFlat index after data is loaded
        print("\nCreating IVFFlat vector index...")
        async with engine.begin() as conn:
            await conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_chunk_embedding_ivfflat "
                "ON chunks USING ivfflat (embedding vector_cosine_ops) "
                "WITH (lists = 100)"
            ))
        print("IVFFlat index created.")

    await engine.dispose()

    print(f"\nSeed complete!")
    print(f"  Mode: {mode}")
    print(f"  Documents: {len(SEED_DOCUMENTS)}")
    print(f"  Total chunks: {total_chunks}")
    print(f"  Total tokens: {total_tokens}")
    print(f"  Conversations: 2")
    print(f"  Admin login: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(main())
