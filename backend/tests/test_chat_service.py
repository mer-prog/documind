"""Tests for the chat service (mock response builder + conversation scoping)."""

import json
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.chat_service import _build_mock_response, stream_chat_response
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


class TestStreamChatConversationScope:
    """Conversation lookup must be scoped to the requesting user (IDOR guard)."""

    def _make_db(self, captured_statements: list) -> MagicMock:
        """A mock session whose conversation lookup finds nothing."""

        async def fake_execute(statement, *args, **kwargs):
            captured_statements.append(statement)
            result = MagicMock()
            result.scalar_one_or_none.return_value = None
            return result

        db = MagicMock()
        db.execute = AsyncMock(side_effect=fake_execute)
        return db

    async def test_foreign_conversation_id_is_rejected(self) -> None:
        """A conversation_id not owned by the user yields an error event only."""
        captured: list = []
        db = self._make_db(captured)

        events = []
        async for event in stream_chat_response(
            db=db,
            user_id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
            message="What is the vacation policy?",
            conversation_id=uuid.uuid4(),
        ):
            events.append(event)

        assert len(events) == 1
        payload = json.loads(events[0].removeprefix("data: ").strip())
        assert payload["type"] == "error"
        db.add.assert_not_called()  # nothing persisted

    async def test_conversation_lookup_filters_by_user_id(self) -> None:
        """The SELECT must filter on both conversation id and user_id."""
        captured: list = []
        db = self._make_db(captured)

        async for _ in stream_chat_response(
            db=db,
            user_id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
            message="What is the vacation policy?",
            conversation_id=uuid.uuid4(),
        ):
            pass

        assert len(captured) == 1
        compiled = str(captured[0])
        assert "conversations.id" in compiled
        assert "conversations.user_id" in compiled
