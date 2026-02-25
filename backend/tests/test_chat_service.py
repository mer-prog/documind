"""Tests for the chat service (mock response builder)."""

import uuid

import pytest

from app.services.chat_service import _build_mock_response
from app.services.search_service import SearchResult


def _make_search_result(**kwargs) -> SearchResult:
    return SearchResult(
        chunk_id=kwargs.get("chunk_id", uuid.uuid4()),
        document_name=kwargs.get("document_name", "handbook.md"),
        page_number=kwargs.get("page_number"),
        heading=kwargs.get("heading"),
        text_snippet=kwargs.get("text_snippet", "Some relevant text from the document."),
        relevance_score=kwargs.get("relevance_score", 0.85),
    )


class TestBuildMockResponse:
    """Template-based response generation for demo mode."""

    def test_no_results_returns_fallback(self) -> None:
        response = _build_mock_response([], "What is PTO?")
        assert "couldn't find" in response.lower()

    def test_includes_source_references(self) -> None:
        results = [_make_search_result(document_name="policy.md")]
        response = _build_mock_response(results, "query")
        assert "policy.md" in response

    def test_includes_page_number_when_available(self) -> None:
        results = [_make_search_result(page_number=5)]
        response = _build_mock_response(results, "query")
        assert "Page 5" in response

    def test_includes_heading_when_available(self) -> None:
        results = [_make_search_result(heading="Vacation Policy")]
        response = _build_mock_response(results, "query")
        assert "Vacation Policy" in response

    def test_limits_to_three_sources(self) -> None:
        results = [_make_search_result(document_name=f"doc{i}.md") for i in range(5)]
        response = _build_mock_response(results, "query")
        assert "doc0.md" in response
        assert "doc2.md" in response
        assert "doc4.md" not in response  # Only top 3

    def test_includes_demo_mode_notice(self) -> None:
        results = [_make_search_result()]
        response = _build_mock_response(results, "query")
        assert "demo mode" in response.lower()

    def test_includes_text_snippet(self) -> None:
        results = [_make_search_result(text_snippet="Employees get 20 PTO days.")]
        response = _build_mock_response(results, "query")
        assert "20 PTO days" in response
