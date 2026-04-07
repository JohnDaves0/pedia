from pypdf import PdfReader


def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """Extract text from each page of a PDF.

    Returns:
        List of {"page": int, "text": str} dicts (skips empty pages).
    """
    reader = PdfReader(pdf_path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append({"page": i + 1, "text": text})
    return pages
