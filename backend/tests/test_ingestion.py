import os
import tempfile
import pytest

from app.services.ingestion.chunker import chunk_text
from app.services.ingestion.extractor import extract_text_from_pdf


def test_chunk_text_basic():
    text = " ".join([f"word{i}" for i in range(1000)])
    chunks = chunk_text(text, page=1, filename="test.pdf")
    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk["page"] == 1
        assert chunk["filename"] == "test.pdf"
        assert len(chunk["text"]) > 0


def test_chunk_text_overlap():
    """Chunks should overlap — the last words of one chunk appear at the start of the next."""
    from app.config import settings

    text = " ".join([f"w{i}" for i in range(settings.chunk_size + settings.chunk_overlap + 10)])
    chunks = chunk_text(text, page=1, filename="test.pdf")
    assert len(chunks) >= 2

    first_words = chunks[0]["text"].split()
    second_words = chunks[1]["text"].split()
    # The second chunk should start with words that appeared near the end of the first
    overlap_words = first_words[-settings.chunk_overlap :]
    assert second_words[: settings.chunk_overlap] == overlap_words


def test_chunk_text_short_input():
    """A short text should produce exactly one chunk."""
    text = "hello world this is a short text"
    chunks = chunk_text(text, page=2, filename="doc.pdf")
    assert len(chunks) == 1


def test_extract_text_missing_file():
    with pytest.raises(Exception):
        extract_text_from_pdf("/nonexistent/path.pdf")
