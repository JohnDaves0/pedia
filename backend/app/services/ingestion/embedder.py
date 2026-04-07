import uuid
from pathlib import Path

from app.services.ingestion.extractor import extract_text_from_pdf
from app.services.ingestion.chunker import chunk_text
from app.services.search.vector_search import get_collection


def ingest_pdf(pdf_path: str) -> int:
    """Ingest a single PDF into the vector store.

    Deletes any previously ingested chunks for this file before re-ingesting.

    Returns:
        Number of chunks ingested.
    """
    collection = get_collection()
    filename = Path(pdf_path).name

    # Remove stale chunks for this file
    existing = collection.get(where={"filename": filename})
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    pages = extract_text_from_pdf(pdf_path)
    all_chunks: list[dict] = []
    for page_data in pages:
        all_chunks.extend(chunk_text(page_data["text"], page_data["page"], filename))

    if not all_chunks:
        return 0

    collection.add(
        documents=[c["text"] for c in all_chunks],
        metadatas=[{"page": c["page"], "filename": c["filename"]} for c in all_chunks],
        ids=[str(uuid.uuid4()) for _ in all_chunks],
    )
    return len(all_chunks)
