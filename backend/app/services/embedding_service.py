"""
Dual-mode embedding service.

When OPENAI_API_KEY is set, uses OpenAI text-embedding-3-small.
When unset, generates deterministic hash-based pseudo-vectors so the
full pipeline (ingest → search → chat) works without any external API.
"""

import hashlib
import math

from app.config import settings


def generate_mock_embedding(text: str, dimensions: int = 1536) -> list[float]:
    """Generate a deterministic pseudo-embedding from text using SHA-256 hashing."""
    words = text.lower().split()
    vector: list[float] = []
    for i in range(dimensions):
        seed_text = f"{' '.join(words[:min(10, len(words))])}_{i}"
        hash_val = int(hashlib.sha256(seed_text.encode()).hexdigest(), 16)
        value = (hash_val % 10000) / 5000.0 - 1.0
        vector.append(value)
    norm = math.sqrt(sum(v * v for v in vector))
    if norm > 0:
        vector = [v / norm for v in vector]
    return vector


def _get_openai_client():
    """Lazy-initialise the OpenAI async client (import only when needed)."""
    from openai import AsyncOpenAI

    return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def get_embedding(text: str) -> list[float]:
    """Return an embedding vector for *text*."""
    if settings.OPENAI_API_KEY:
        client = _get_openai_client()
        response = await client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=text,
        )
        return response.data[0].embedding
    return generate_mock_embedding(text, settings.EMBEDDING_DIMENSIONS)


async def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Return embedding vectors for a list of texts."""
    if not texts:
        return []

    if settings.OPENAI_API_KEY:
        client = _get_openai_client()
        all_embeddings: list[list[float]] = []
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = await client.embeddings.create(
                model=settings.EMBEDDING_MODEL,
                input=batch,
            )
            all_embeddings.extend([item.embedding for item in response.data])
        return all_embeddings

    return [
        generate_mock_embedding(t, settings.EMBEDDING_DIMENSIONS) for t in texts
    ]
