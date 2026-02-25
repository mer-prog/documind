"""Tests for the document ingestion pipeline (parsing & chunking).

The ingest_service module initializes tiktoken at module level, which
requires network access to download the BPE encoding. We mock tiktoken
before importing to isolate the pure parsing/chunking logic under test.
"""

import sys
from unittest.mock import MagicMock

import pytest

# Mock tiktoken to avoid network-dependent BPE download
_tiktoken_mock = MagicMock()
_tiktoken_mock.get_encoding.return_value.encode = lambda text: text.split()
sys.modules.setdefault("tiktoken", _tiktoken_mock)

from app.services.ingest_service import (
    RawChunk,
    chunk_text,
    parse_markdown,
)


# ── Markdown Parsing ──


class TestParseMarkdown:
    """Heading-aware Markdown splitting."""

    def test_splits_by_headings(self) -> None:
        md = "# Intro\nFirst paragraph.\n\n# Policy\nSecond paragraph."
        chunks = parse_markdown(md)
        assert len(chunks) == 2
        assert chunks[0].heading == "Intro"
        assert chunks[1].heading == "Policy"

    def test_splits_by_paragraphs_within_section(self) -> None:
        md = "# Section\nParagraph one.\n\nParagraph two."
        chunks = parse_markdown(md)
        assert len(chunks) == 2
        assert chunks[0].content == "Paragraph one."
        assert chunks[1].content == "Paragraph two."

    def test_handles_h2_and_h3(self) -> None:
        md = "## Sub\nContent A.\n\n### Deep\nContent B."
        chunks = parse_markdown(md)
        assert any(c.heading == "Sub" for c in chunks)
        assert any(c.heading == "Deep" for c in chunks)

    def test_text_without_headings(self) -> None:
        md = "Just a plain paragraph.\n\nAnother paragraph."
        chunks = parse_markdown(md)
        assert len(chunks) == 2
        assert chunks[0].heading is None

    def test_empty_input(self) -> None:
        assert parse_markdown("") == []

    def test_heading_only_no_body(self) -> None:
        md = "# Title Only"
        chunks = parse_markdown(md)
        assert len(chunks) == 0  # heading without body is skipped

    def test_preserves_content_integrity(self) -> None:
        md = "# FAQ\nWhat is PTO? Paid time off allows employees to take leave."
        chunks = parse_markdown(md)
        assert len(chunks) == 1
        assert "Paid time off" in chunks[0].content

    def test_multiline_paragraphs(self) -> None:
        md = "# Docs\nLine one.\nLine two still same paragraph."
        chunks = parse_markdown(md)
        assert len(chunks) == 1
        assert "Line one" in chunks[0].content
        assert "Line two" in chunks[0].content


# ── Chunking with Overlap ──
# Note: count_tokens is mocked (word-split), so CHUNK_SIZE=500 means 500 words


class TestChunkText:
    """Size-based splitting with overlap at sentence boundaries."""

    def test_small_chunk_passes_through(self) -> None:
        """Chunks under CHUNK_SIZE should not be split."""
        raw = [RawChunk(content="Short text.", heading="Test")]
        result = chunk_text(raw)
        assert len(result) == 1
        assert result[0].heading == "Test"
        assert "Short text." in result[0].content

    def test_preserves_page_number(self) -> None:
        raw = [RawChunk(content="PDF content here.", page_number=3)]
        result = chunk_text(raw)
        assert result[0].page_number == 3

    def test_chunk_indices_are_sequential(self) -> None:
        raw = [
            RawChunk(content="First chunk content."),
            RawChunk(content="Second chunk content."),
        ]
        result = chunk_text(raw)
        indices = [c.chunk_index for c in result]
        assert indices == list(range(len(indices)))

    def test_long_text_gets_split(self) -> None:
        """A text with >500 words should produce multiple chunks."""
        sentences = [f"Sentence number {i} has some words in it." for i in range(120)]
        long_text = " ".join(sentences)
        raw = [RawChunk(content=long_text)]
        result = chunk_text(raw)
        assert len(result) >= 2

    def test_overlap_creates_shared_content(self) -> None:
        """Consecutive chunks should share overlapping text."""
        sentences = [f"This is detailed sentence number {i} with enough tokens." for i in range(120)]
        long_text = " ".join(sentences)
        raw = [RawChunk(content=long_text)]
        result = chunk_text(raw)
        if len(result) >= 2:
            last_words_0 = set(result[0].content.split()[-10:])
            first_words_1 = set(result[1].content.split()[:20])
            overlap = last_words_0 & first_words_1
            assert len(overlap) > 0, "Expected overlap between consecutive chunks"

    def test_token_count_is_set(self) -> None:
        raw = [RawChunk(content="Count my tokens please.")]
        result = chunk_text(raw)
        assert result[0].token_count > 0

    def test_empty_input(self) -> None:
        assert chunk_text([]) == []
