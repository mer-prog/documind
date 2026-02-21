"""
Seed script for DocuMind.

Run from the backend directory:
    python -m seed.seed

Requires:
    - DATABASE_URL set in .env or environment
    - OPENAI_API_KEY set in .env or environment
    - Database with migrations applied (alembic upgrade head)
"""

import asyncio
import os
import sys
import uuid
from pathlib import Path

import bcrypt
from openai import AsyncOpenAI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.models import Base, Chunk, Document, User, Workspace
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
WORKSPACE_NAME = "DocuMind Workspace"


async def main():
    print("Starting DocuMind seed...")
    print(f"Database: {settings.DATABASE_URL[:50]}...")

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

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

            all_embeddings = []
            batch_size = 100
            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                response = await openai_client.embeddings.create(
                    model=settings.EMBEDDING_MODEL,
                    input=batch,
                )
                all_embeddings.extend([item.embedding for item in response.data])

            # Create chunk records
            for i, (pc, emb) in enumerate(zip(processed_chunks, all_embeddings)):
                chunk = Chunk(
                    id=uuid.uuid4(),
                    document_id=doc_id,
                    content=pc.content,
                    token_count=pc.token_count,
                    page_number=pc.page_number,
                    heading=pc.heading,
                    chunk_index=pc.chunk_index,
                    embedding=emb,
                )
                db.add(chunk)

            document.chunk_count = len(processed_chunks)
            total_chunks += len(processed_chunks)
            total_tokens += sum(c.token_count for c in processed_chunks)

            await db.flush()
            print(f"  Done: {len(processed_chunks)} chunks, {sum(c.token_count for c in processed_chunks)} tokens")

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
    print(f"  Documents: {len(SEED_DOCUMENTS)}")
    print(f"  Total chunks: {total_chunks}")
    print(f"  Total tokens: {total_tokens}")
    print(f"  Admin login: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(main())
