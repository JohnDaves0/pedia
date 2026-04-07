import pickle
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import settings

_vectorizer: TfidfVectorizer | None = None
_matrix = None
_documents: list[dict] = []


def _index_path() -> Path:
    return Path(settings.chroma_db_path) / "index.pkl"


def _load_index() -> None:
    global _vectorizer, _matrix, _documents
    path = _index_path()
    if path.exists():
        with open(path, "rb") as f:
            data = pickle.load(f)
        _vectorizer = data["vectorizer"]
        _matrix = data["matrix"]
        _documents = data["documents"]


def _save_index() -> None:
    path = _index_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(
            {"vectorizer": _vectorizer, "matrix": _matrix, "documents": _documents},
            f,
        )


def clear_file(filename: str) -> None:
    """Remove all chunks for a given filename from the in-memory index."""
    global _documents
    _documents = [d for d in _documents if d["filename"] != filename]


def add_documents(docs: list[dict]) -> None:
    """Add chunks and rebuild the TF-IDF index.

    Each doc must have: {"text": str, "filename": str, "page": int}
    """
    global _vectorizer, _matrix, _documents
    _documents.extend(docs)
    texts = [d["text"] for d in _documents]
    _vectorizer = TfidfVectorizer(stop_words="english", max_features=50_000)
    _matrix = _vectorizer.fit_transform(texts)
    _save_index()


def search(query: str) -> list[dict]:
    """Return the top-k most relevant chunks for a query."""
    global _vectorizer, _matrix, _documents
    if _vectorizer is None:
        _load_index()
    if not _documents or _vectorizer is None:
        return []

    query_vec = _vectorizer.transform([query])
    scores = cosine_similarity(query_vec, _matrix)[0]
    top_indices = scores.argsort()[::-1][: settings.top_k_results]

    return [_documents[i] for i in top_indices if scores[i] > 0.0]
