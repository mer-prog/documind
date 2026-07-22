"""Tests for the hybrid search engine (RRF fusion logic + concurrency safety)."""

import asyncio
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import search_service
from app.services.search_service import SearchResult, _rrf_fuse


def _make_result(rid: str | None = None, **kwargs) -> dict:
    """Helper to create a search result dict."""
    return {
        "id": uuid.UUID(rid) if rid else uuid.uuid4(),
        "content": kwargs.get("content", "Some chunk text"),
        "page_number": kwargs.get("page_number"),
        "heading": kwargs.get("heading"),
        "document_id": uuid.uuid4(),
        "filename": kwargs.get("filename", "doc.md"),
        "score": kwargs.get("score", 0.9),
    }


class TestRRFFuse:
    """Reciprocal Rank Fusion: score = Σ 1/(rank + 1 + k)."""

    def test_combines_results_from_both_sources(self) -> None:
        id_a = str(uuid.uuid4())
        id_b = str(uuid.uuid4())
        vec = [_make_result(rid=id_a)]
        kw = [_make_result(rid=id_b)]
        fused = _rrf_fuse(vec, kw, k=60)
        ids = {str(r["id"]) for r in fused}
        assert id_a in ids
        assert id_b in ids

    def test_duplicate_gets_higher_score(self) -> None:
        """A result appearing in both rankings should score higher than one in only one."""
        shared_id = str(uuid.uuid4())
        only_vec_id = str(uuid.uuid4())
        vec = [_make_result(rid=shared_id), _make_result(rid=only_vec_id)]
        kw = [_make_result(rid=shared_id)]
        fused = _rrf_fuse(vec, kw, k=60)
        scores = {str(r["id"]): r["rrf_score"] for r in fused}
        assert scores[shared_id] > scores[only_vec_id]

    def test_rrf_score_formula(self) -> None:
        """Verify the RRF score matches 1/(rank + 1 + k)."""
        id1 = str(uuid.uuid4())
        id2 = str(uuid.uuid4())
        vec = [_make_result(rid=id1), _make_result(rid=id2)]
        kw = []
        fused = _rrf_fuse(vec, kw, k=60)
        scores = {str(r["id"]): r["rrf_score"] for r in fused}
        # rank 0 → 1/(0+1+60) = 1/61
        assert abs(scores[id1] - 1.0 / 61) < 1e-9
        # rank 1 → 1/(1+1+60) = 1/62
        assert abs(scores[id2] - 1.0 / 62) < 1e-9

    def test_sorted_by_score_descending(self) -> None:
        results = [_make_result() for _ in range(5)]
        fused = _rrf_fuse(results, [], k=60)
        scores = [r["rrf_score"] for r in fused]
        assert scores == sorted(scores, reverse=True)

    def test_empty_inputs(self) -> None:
        assert _rrf_fuse([], [], k=60) == []

    def test_only_vector_results(self) -> None:
        vec = [_make_result() for _ in range(3)]
        fused = _rrf_fuse(vec, [], k=60)
        assert len(fused) == 3

    def test_only_keyword_results(self) -> None:
        kw = [_make_result() for _ in range(3)]
        fused = _rrf_fuse([], kw, k=60)
        assert len(fused) == 3

    def test_custom_k_parameter(self) -> None:
        """Different k values should produce different scores."""
        rid = str(uuid.uuid4())
        # Create separate dicts because _rrf_fuse mutates results in-place
        vec_a = [_make_result(rid=rid)]
        vec_b = [_make_result(rid=rid)]
        fused_k10 = _rrf_fuse(vec_a, [], k=10)
        fused_k100 = _rrf_fuse(vec_b, [], k=100)
        # Lower k → higher score for top results: 1/12 > 1/102
        assert fused_k10[0]["rrf_score"] > fused_k100[0]["rrf_score"]

    def test_deduplication(self) -> None:
        """Same ID in both lists should appear only once in output."""
        shared_id = str(uuid.uuid4())
        vec = [_make_result(rid=shared_id)]
        kw = [_make_result(rid=shared_id)]
        fused = _rrf_fuse(vec, kw, k=60)
        assert len(fused) == 1

    def test_combined_score_is_sum(self) -> None:
        """Score for a result in both lists = sum of individual RRF scores."""
        shared_id = str(uuid.uuid4())
        vec = [_make_result(rid=shared_id)]
        kw = [_make_result(rid=shared_id)]
        fused = _rrf_fuse(vec, kw, k=60)
        expected = 1.0 / 61 + 1.0 / 61  # rank 0 in both
        assert abs(fused[0]["rrf_score"] - expected) < 1e-9


class TestHybridSearchConcurrency:
    """A single AsyncSession does not support concurrent operations, so
    hybrid_search must give each concurrent query its own session."""

    async def test_each_search_gets_its_own_session(self, monkeypatch) -> None:
        sessions: list = []
        keyword_started = asyncio.Event()

        async def fake_embedding(text: str) -> list[float]:
            return [0.0] * 4

        async def fake_vector(db, embedding, workspace_id, limit=20):
            sessions.append(db)
            # Block until the keyword search has started: proves the two
            # searches actually overlap (sequential execution would hit
            # the timeout below and fail instead of hanging).
            await asyncio.wait_for(keyword_started.wait(), timeout=5)
            return [_make_result()]

        async def fake_keyword(db, query, workspace_id, limit=20):
            sessions.append(db)
            keyword_started.set()
            return [_make_result()]

        monkeypatch.setattr(
            search_service.embedding_service, "get_embedding", fake_embedding
        )
        monkeypatch.setattr(search_service, "_vector_search", fake_vector)
        monkeypatch.setattr(search_service, "_keyword_search", fake_keyword)

        results = await asyncio.wait_for(
            search_service.hybrid_search("remote work policy", uuid.uuid4()),
            timeout=5,
        )

        assert len(sessions) == 2
        assert sessions[0] is not sessions[1]
        assert all(isinstance(s, AsyncSession) for s in sessions)
        assert len(results) == 2
        assert all(isinstance(r, SearchResult) for r in results)
