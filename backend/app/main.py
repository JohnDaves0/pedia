from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, pdfs

app = FastAPI(title="Pedia PDF Assistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(pdfs.router)


@app.get("/health")
def health():
    return {"status": "ok"}
