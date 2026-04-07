from pathlib import Path

from app.services.ingestion.extractor import extract_text_from_pdf
from app.services.ingestion.chunker import chunk_text
from app.services.search.vector_search import clear_file, add_documents


def ingest_pdf(pdf_path: str) -> int:
    """Ingest a single PDF into the search index.

    Removes any previously ingested chunks for this file first.

    Returns:
        Number of chunks ingested.
    """
    filename = Path(pdf_path).name
    clear_file(filename)

    pages = extract_text_from_pdf(pdf_path)
    all_chunks: list[dict] = []
    for page_data in pages:
        all_chunks.extend(chunk_text(page_data["text"], page_data["page"], filename))

    if not all_chunks:
        return 0

    add_documents(all_chunks)
    return len(all_chunks)
