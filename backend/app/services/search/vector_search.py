import chromadb
from chromadb.utils import embedding_functions

from app.config import settings

_collection = None


def get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=settings.chroma_db_path)
        ef = embedding_functions.DefaultEmbeddingFunction()
        _collection = client.get_or_create_collection(
            name="pdf_chunks",
            embedding_function=ef,
        )
    return _collection


def search(query: str) -> list[dict]:
    """Return the top-k most relevant chunks for a query.

    Returns:
        List of {"text": str, "filename": str, "page": int} dicts.
    """
    collection = get_collection()
    count = collection.count()
    if count == 0:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=min(settings.top_k_results, count),
    )

    chunks = []
    for i, doc in enumerate(results["documents"][0]):
        meta = results["metadatas"][0][i]
        chunks.append(
            {
                "text": doc,
                "filename": meta.get("filename", "unknown"),
                "page": meta.get("page", 0),
            }
        )
    return chunks
