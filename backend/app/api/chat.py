from fastapi import APIRouter

from app.agent.agent import run_agent
from app.models.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Send a message and receive an AI response, optionally backed by PDF search."""
    response_text, sources = run_agent(request.message, request.session_id)
    return ChatResponse(
        response=response_text,
        sources=sources,
        session_id=request.session_id,
    )
