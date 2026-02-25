"""Tests for the hybrid search engine (RRF fusion logic)."""

import uuid

import pytest

from app.services.search_service import _rrf_fuse


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
