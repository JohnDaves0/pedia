import pytest

from app.services.search.vector_search import (
    add_documents,
    clear_file,
    search,
    _load_index,
)
import app.services.search.vector_search as vs


@pytest.fixture(autouse=True)
def reset_index(tmp_path, monkeypatch):
    """Isolate each test with a clean in-memory index and temp storage."""
    monkeypatch.setattr("app.config.settings.chroma_db_path", str(tmp_path))
    vs._vectorizer = None
    vs._matrix = None
    vs._documents = []
    yield
    vs._vectorizer = None
    vs._matrix = None
    vs._documents = []


def test_search_empty_index():
    assert search("algorithm") == []


def test_search_returns_results():
    add_documents([
        {"text": "Binary search is an efficient algorithm for sorted arrays.",
         "filename": "ch1.pdf", "page": 3}
    ])
    results = search("binary search")
    assert len(results) == 1
    assert results[0]["filename"] == "ch1.pdf"
    assert results[0]["page"] == 3


def test_search_respects_top_k(monkeypatch):
    monkeypatch.setattr("app.config.settings.top_k_results", 2)
    docs = [
        {"text": f"Sorting algorithm document number {i}.", "filename": f"ch{i}.pdf", "page": i}
        for i in range(5)
    ]
    add_documents(docs)
    results = search("sorting")
    assert len(results) <= 2


def test_clear_file_removes_chunks():
    add_documents([
        {"text": "Merge sort divides the array.", "filename": "ch5.pdf", "page": 1},
        {"text": "Quick sort uses a pivot element.", "filename": "ch6.pdf", "page": 1},
    ])
    clear_file("ch5.pdf")
    # Re-add remaining and rebuild
    remaining = [d for d in vs._documents]
    assert all(d["filename"] != "ch5.pdf" for d in remaining)


def test_index_persists_to_disk(tmp_path, monkeypatch):
    monkeypatch.setattr("app.config.settings.chroma_db_path", str(tmp_path))
    add_documents([
        {"text": "Heap sort builds a max-heap.", "filename": "ch7.pdf", "page": 2}
    ])
    # Reset in-memory state and reload from disk
    vs._vectorizer = None
    vs._matrix = None
    vs._documents = []
    _load_index()
    assert len(vs._documents) == 1
    assert vs._documents[0]["filename"] == "ch7.pdf"
