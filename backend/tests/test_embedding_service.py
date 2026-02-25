"""Tests for the dual-mode embedding service."""

import math

import pytest

from app.services.embedding_service import generate_mock_embedding


class TestGenerateMockEmbedding:
    """Deterministic hash-based pseudo-embedding generation."""

    def test_returns_correct_dimensions(self) -> None:
        vec = generate_mock_embedding("hello world")
        assert len(vec) == 1536

    def test_custom_dimensions(self) -> None:
        vec = generate_mock_embedding("test", dimensions=768)
        assert len(vec) == 768

    def test_deterministic_output(self) -> None:
        """Same text must always produce the same vector."""
        v1 = generate_mock_embedding("the company handbook")
        v2 = generate_mock_embedding("the company handbook")
        assert v1 == v2

    def test_different_text_different_vectors(self) -> None:
        v1 = generate_mock_embedding("vacation policy")
        v2 = generate_mock_embedding("expense reports")
        assert v1 != v2

    def test_l2_normalized(self) -> None:
        """Output vector must be unit-length (L2 norm ≈ 1.0)."""
        vec = generate_mock_embedding("normalize me")
        norm = math.sqrt(sum(v * v for v in vec))
        assert abs(norm - 1.0) < 1e-6

    def test_values_in_range(self) -> None:
        """All components should be in [-1, 1] after normalization."""
        vec = generate_mock_embedding("range check")
        assert all(-1.0 <= v <= 1.0 for v in vec)

    def test_empty_string(self) -> None:
        """Empty input should not crash."""
        vec = generate_mock_embedding("")
        assert len(vec) == 1536
        norm = math.sqrt(sum(v * v for v in vec))
        assert abs(norm - 1.0) < 1e-6

    def test_whitespace_only(self) -> None:
        vec = generate_mock_embedding("   ")
        assert len(vec) == 1536

    def test_case_insensitive(self) -> None:
        """Embedding uses .lower(), so case should not matter."""
        v1 = generate_mock_embedding("Hello World")
        v2 = generate_mock_embedding("hello world")
        assert v1 == v2
