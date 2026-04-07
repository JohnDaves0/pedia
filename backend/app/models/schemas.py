from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class Source(BaseModel):
    filename: str
    page: int
    excerpt: str


class ChatResponse(BaseModel):
    response: str
    sources: list[Source] = []
    session_id: str


class PDFInfo(BaseModel):
    filename: str
    chunks: int


class IngestResponse(BaseModel):
    ingested: list[PDFInfo]
    total_chunks: int
