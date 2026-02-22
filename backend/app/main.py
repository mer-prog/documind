import uuid
from pathlib import Path

import bcrypt
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Chunk, Conversation, Document, Message, User, Workspace
from app.routers import analytics, auth, chat, conversations, documents
from app.services import embedding_service
from app.services.ingest_service import chunk_text, parse_markdown

app = FastAPI(title="DocuMind API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(conversations.router, prefix="/api", tags=["conversations"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

SEED_DATA_DIR = Path(__file__).resolve().parent.parent / "seed" / "data"


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/mode")
async def get_mode():
    is_live = bool(settings.OPENAI_API_KEY)
    return {
        "mode": "live" if is_live else "demo",
        "model": settings.CHAT_MODEL if is_live else None,
    }


@app.post("/api/seed")
async def seed_database(db: AsyncSession = Depends(get_db)):
    # Check if already seeded
    result = await db.execute(select(User).limit(1))
    if result.scalars().first() is not None:
        return {"status": "already seeded"}

    # Create workspace
    workspace_id = uuid.uuid4()
    workspace = Workspace(id=workspace_id, name="Acme Corp Knowledge Base")
    db.add(workspace)
    await db.flush()

    # Create demo admin user
    hashed_pw = bcrypt.hashpw(
        b"demo1234", bcrypt.gensalt()
    ).decode("utf-8")
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        email="admin@documind.dev",
        hashed_password=hashed_pw,
        name="Admin User",
        role="admin",
        workspace_id=workspace_id,
    )
    db.add(user)
    await db.flush()

    # Seed documents from seed/data/ directory
    seed_filenames = [
        "company-handbook.md",
        "product-roadmap.md",
        "api-documentation.md",
    ]
    first_doc_chunks: list[dict] = []

    for filename in seed_filenames:
        filepath = SEED_DATA_DIR / filename
        if not filepath.exists():
            continue

        content = filepath.read_text(encoding="utf-8")
        file_bytes = content.encode("utf-8")

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

        raw_chunks = parse_markdown(content)
        processed_chunks = chunk_text(raw_chunks)

        embeddings = [
            embedding_service.generate_mock_embedding(
                c.content, settings.EMBEDDING_DIMENSIONS
            )
            for c in processed_chunks
        ]

        for i, (pc, emb) in enumerate(zip(processed_chunks, embeddings)):
            chunk_id = uuid.uuid4()
            chunk = Chunk(
                id=chunk_id,
                document_id=doc_id,
                content=pc.content,
                token_count=pc.token_count,
                page_number=pc.page_number,
                heading=pc.heading,
                chunk_index=pc.chunk_index,
                embedding=emb,
            )
            db.add(chunk)
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
        await db.flush()

    # Create sample conversations
    conv1_id = uuid.uuid4()
    db.add(Conversation(
        id=conv1_id,
        user_id=user_id,
        workspace_id=workspace_id,
        title="Remote work policy question",
        message_count=2,
    ))
    await db.flush()

    db.add(Message(
        id=uuid.uuid4(),
        conversation_id=conv1_id,
        role="user",
        content="What is the remote work policy?",
        token_count=7,
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
    ))

    conv2_id = uuid.uuid4()
    db.add(Conversation(
        id=conv2_id,
        user_id=user_id,
        workspace_id=workspace_id,
        title="Q1 product roadmap milestones",
        message_count=2,
    ))
    await db.flush()

    db.add(Message(
        id=uuid.uuid4(),
        conversation_id=conv2_id,
        role="user",
        content="What are the key milestones for Q1?",
        token_count=9,
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
    ))

    return {"status": "seeded"}
