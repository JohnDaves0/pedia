from fastapi import APIRouter, HTTPException
from pathlib import Path

from app.config import settings
from app.services.ingestion.embedder import ingest_pdf
from app.models.schemas import PDFInfo, IngestResponse

router = APIRouter(prefix="/pdfs", tags=["pdfs"])


@router.post("/ingest", response_model=IngestResponse, status_code=200)
def ingest_all_pdfs():
    """Scan the configured PDF folder and ingest all PDFs into the vector store."""
    folder = Path(settings.pdf_folder)
    pdf_files = sorted(folder.glob("*.pdf"))

    if not pdf_files:
        raise HTTPException(status_code=404, detail=f"No PDFs found in {folder}")

    ingested: list[PDFInfo] = []
    total_chunks = 0

    for pdf_path in pdf_files:
        n = ingest_pdf(str(pdf_path))
        ingested.append(PDFInfo(filename=pdf_path.name, chunks=n))
        total_chunks += n

    return IngestResponse(ingested=ingested, total_chunks=total_chunks)


@router.get("", response_model=list[PDFInfo])
def list_pdfs():
    """List PDFs available in the configured folder (not necessarily ingested yet)."""
    folder = Path(settings.pdf_folder)
    return [
        PDFInfo(filename=p.name, chunks=0)
        for p in sorted(folder.glob("*.pdf"))
    ]
