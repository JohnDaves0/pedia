from app.config import settings


def chunk_text(text: str, page: int, filename: str) -> list[dict]:
    """Split page text into overlapping word-based chunks.

    Returns:
        List of {"text": str, "page": int, "filename": str} dicts.
    """
    size = settings.chunk_size
    overlap = settings.chunk_overlap
    words = text.split()
    chunks = []

    i = 0
    while i < len(words):
        chunk_words = words[i : i + size]
        chunks.append(
            {
                "text": " ".join(chunk_words),
                "page": page,
                "filename": filename,
            }
        )
        if i + size >= len(words):
            break
        i += size - overlap

    return chunks
