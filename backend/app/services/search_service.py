import asyncio
import uuid
from dataclasses import dataclass

from openai import AsyncOpenAI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings

openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


@dataclass
class SearchResult:
    chunk_id: uuid.UUID
    document_name: str
    page_number: int | None
    heading: str | None
    text_snippet: str
    relevance_score: float


async def _vector_search(
    db: AsyncSession,
    query_embedding: list[float],
    workspace_id: uuid.UUID,
    limit: int = 20,
) -> list[dict]:
    sql = text("""
        SELECT c.id, c.content, c.page_number, c.heading, c.document_id, d.filename,
               1 - (c.embedding <=> :query_vector::vector) AS vector_score
        FROM chunks c
        JOIN documents d ON c.document_id = d.id
        WHERE d.workspace_id = :workspace_id
          AND c.embedding IS NOT NULL
        ORDER BY c.embedding <=> :query_vector::vector
        LIMIT :limit
    """)
    result = await db.execute(
        sql,
        {
            "query_vector": str(query_embedding),
            "workspace_id": str(workspace_id),
            "limit": limit,
        },
    )
    rows = result.fetchall()
    return [
        {
            "id": row[0],
            "content": row[1],
            "page_number": row[2],
            "heading": row[3],
            "document_id": row[4],
            "filename": row[5],
            "score": float(row[6]) if row[6] else 0.0,
        }
        for row in rows
    ]


async def _keyword_search(
    db: AsyncSession,
    query: str,
    workspace_id: uuid.UUID,
    limit: int = 20,
) -> list[dict]:
    sql = text("""
        SELECT c.id, c.content, c.page_number, c.heading, c.document_id, d.filename,
               similarity(c.content, :query) AS trgm_score
        FROM chunks c
        JOIN documents d ON c.document_id = d.id
        WHERE d.workspace_id = :workspace_id
          AND similarity(c.content, :query) > 0.05
        ORDER BY trgm_score DESC
        LIMIT :limit
    """)
    result = await db.execute(
        sql,
        {
            "query": query,
            "workspace_id": str(workspace_id),
            "limit": limit,
        },
    )
    rows = result.fetchall()
    return [
        {
            "id": row[0],
            "content": row[1],
            "page_number": row[2],
            "heading": row[3],
            "document_id": row[4],
            "filename": row[5],
            "score": float(row[6]) if row[6] else 0.0,
        }
        for row in rows
    ]


def _rrf_fuse(
    vector_results: list[dict],
    keyword_results: list[dict],
    k: int = 60,
) -> list[dict]:
    scores: dict[str, float] = {}
    all_results: dict[str, dict] = {}

    for rank, result in enumerate(vector_results):
        rid = str(result["id"])
        scores[rid] = scores.get(rid, 0) + 1.0 / (rank + 1 + k)
        all_results[rid] = result

    for rank, result in enumerate(keyword_results):
        rid = str(result["id"])
        scores[rid] = scores.get(rid, 0) + 1.0 / (rank + 1 + k)
        all_results[rid] = result

    # Sort by combined score
    sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    fused = []
    for rid, score in sorted_ids:
        r = all_results[rid]
        r["rrf_score"] = score
        fused.append(r)

    return fused


async def hybrid_search(
    db: AsyncSession,
    query: str,
    workspace_id: uuid.UUID,
    top_k: int = 10,
) -> list[SearchResult]:
    # Generate query embedding
    response = await openai_client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=query,
    )
    query_embedding = response.data[0].embedding

    # Run both searches concurrently
    vector_results, keyword_results = await asyncio.gather(
        _vector_search(db, query_embedding, workspace_id),
        _keyword_search(db, query, workspace_id),
    )

    # Fuse with RRF
    fused = _rrf_fuse(vector_results, keyword_results, k=settings.RRF_K)

    # Convert to SearchResult objects
    results = []
    for r in fused[:top_k]:
        results.append(
            SearchResult(
                chunk_id=r["id"],
                document_name=r["filename"],
                page_number=r["page_number"],
                heading=r["heading"],
                text_snippet=r["content"][:500],
                relevance_score=r["rrf_score"],
            )
        )

    return results
