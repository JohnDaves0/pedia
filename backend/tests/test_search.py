import uuid
import pytest

from app.services.search.vector_search import get_collection, search


@pytest.fixture(autouse=True)
def isolated_collection(tmp_path, monkeypatch):
    """Point the vector store at a temp directory for each test."""
    import app.services.search.vector_search as vs

    monkeypatch.setattr("app.config.settings.chroma_db_path", str(tmp_path))
    vs._collection = None  # force re-init
    yield
    vs._collection = None


def test_search_empty_collection():
    results = search("algorithm")
    assert results == []


def test_search_returns_results():
    collection = get_collection()
    collection.add(
        documents=["Binary search is an efficient algorithm for sorted arrays."],
        metadatas=[{"filename": "ch1.pdf", "page": 3}],
        ids=[str(uuid.uuid4())],
    )

    results = search("binary search")
    assert len(results) == 1
    assert results[0]["filename"] == "ch1.pdf"
    assert results[0]["page"] == 3
    assert "binary search" in results[0]["text"].lower()


def test_search_respects_top_k(monkeypatch):
    monkeypatch.setattr("app.config.settings.top_k_results", 2)

    collection = get_collection()
    for i in range(5):
        collection.add(
            documents=[f"Document about sorting algorithm number {i}."],
            metadatas=[{"filename": f"ch{i}.pdf", "page": i}],
            ids=[str(uuid.uuid4())],
        )

    results = search("sorting")
    assert len(results) <= 2
