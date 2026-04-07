import anthropic

from app.config import settings
from app.agent.tools import TOOLS
from app.agent.prompts import SYSTEM_PROMPT
from app.models.schemas import Source
from app.services.search.vector_search import search

client = anthropic.Anthropic(api_key=settings.anthropic_api_key, timeout=55.0)

# In-memory conversation store keyed by session_id.
# Replace with Redis/DB for production multi-process deployments.
_sessions: dict[str, list[dict]] = {}


def _get_history(session_id: str) -> list[dict]:
    return _sessions.setdefault(session_id, [])


def run_agent(message: str, session_id: str) -> tuple[str, list[Source]]:
    """Run one turn of the agent loop.

    Handles multi-step tool calling: Claude may call `search_pdfs` one or more
    times before producing its final text response.

    Returns:
        (response_text, deduplicated_sources)
    """
    history = _get_history(session_id)
    history.append({"role": "user", "content": message})

    all_sources: list[Source] = []

    while True:
        response = client.messages.create(
            model=settings.claude_model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=history,
        )

        if response.stop_reason == "tool_use":
            # Record assistant's tool-use turn in history
            history.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue

                if block.name == "search_pdfs":
                    query = block.input.get("query", "")
                    chunks = search(query)

                    for chunk in chunks:
                        all_sources.append(
                            Source(
                                filename=chunk["filename"],
                                page=chunk["page"],
                                excerpt=chunk["text"][:200],
                            )
                        )

                    if chunks:
                        result_text = "\n\n".join(
                            f"[{c['filename']}, page {c['page']}]\n"
                            f"{c['text'][:settings.search_excerpt_chars]}"
                            for c in chunks
                        )
                    else:
                        result_text = "No relevant content found in the documents."

                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_text,
                        }
                    )

            history.append({"role": "user", "content": tool_results})

        else:
            # Final response — extract text
            final_text = "".join(
                block.text for block in response.content if hasattr(block, "text")
            )
            history.append({"role": "assistant", "content": final_text})

            # Deduplicate sources by (filename, page)
            seen: set[tuple] = set()
            unique_sources: list[Source] = []
            for s in all_sources:
                key = (s.filename, s.page)
                if key not in seen:
                    seen.add(key)
                    unique_sources.append(s)

            return final_text, unique_sources
