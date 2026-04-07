from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    anthropic_api_key: str
    # Default: repo root (where the PDFs live)
    pdf_folder: str = str(Path(__file__).resolve().parent.parent.parent)
    chroma_db_path: str = "./chroma_db"
    claude_model: str = "claude-sonnet-4-6"
    chunk_size: int = 500   # words per chunk
    chunk_overlap: int = 50  # words of overlap between chunks
    top_k_results: int = 3
    search_excerpt_chars: int = 600  # chars of each chunk sent to Claude

    class Config:
        env_file = ".env"


settings = Settings()
