import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture(autouse=True)
def clear_sessions():
    import app.agent.agent as ag
    ag._sessions.clear()
    yield
    ag._sessions.clear()


def _make_text_response(text: str):
    """Build a mock anthropic Messages response with a final text block."""
    block = MagicMock()
    block.type = "text"
    block.text = text

    response = MagicMock()
    response.stop_reason = "end_turn"
    response.content = [block]
    return response


def _make_tool_response(tool_id: str, tool_name: str, tool_input: dict):
    """Build a mock anthropic Messages response that calls a tool."""
    block = MagicMock()
    block.type = "tool_use"
    block.id = tool_id
    block.name = tool_name
    block.input = tool_input

    response = MagicMock()
    response.stop_reason = "tool_use"
    response.content = [block]
    return response


def test_direct_answer_no_search():
    """When Claude returns end_turn immediately, no search is performed."""
    with patch("app.agent.agent.client") as mock_client, \
         patch("app.agent.agent.search") as mock_search:

        mock_client.messages.create.return_value = _make_text_response("Hello!")
        from app.agent.agent import run_agent

        text, sources = run_agent("Hello", "session-1")

        assert text == "Hello!"
        assert sources == []
        mock_search.assert_not_called()


def test_agent_calls_search_tool():
    """When Claude requests tool_use, the agent calls search and feeds results back."""
    with patch("app.agent.agent.client") as mock_client, \
         patch("app.agent.agent.search") as mock_search:

        mock_search.return_value = [
            {"text": "Binary search runs in O(log n).", "filename": "ch1.pdf", "page": 5}
        ]

        mock_client.messages.create.side_effect = [
            _make_tool_response("tool-1", "search_pdfs", {"query": "binary search complexity"}),
            _make_text_response("Binary search is O(log n) — see ch1.pdf page 5."),
        ]

        from app.agent.agent import run_agent

        text, sources = run_agent("What is the complexity of binary search?", "session-2")

        assert "O(log n)" in text
        assert len(sources) == 1
        assert sources[0].filename == "ch1.pdf"
        assert sources[0].page == 5
        mock_search.assert_called_once_with("binary search complexity")


def test_conversation_history_persists():
    """Messages accumulate across turns within the same session."""
    with patch("app.agent.agent.client") as mock_client:
        mock_client.messages.create.return_value = _make_text_response("Sure!")

        from app.agent.agent import run_agent, _sessions

        run_agent("First message", "session-3")
        run_agent("Second message", "session-3")

        history = _sessions["session-3"]
        user_msgs = [m for m in history if m["role"] == "user"]
        assert len(user_msgs) == 2


def test_sources_deduplicated():
    """Duplicate (filename, page) pairs in search results appear only once in sources."""
    with patch("app.agent.agent.client") as mock_client, \
         patch("app.agent.agent.search") as mock_search:

        # Same chunk returned twice (two tool calls)
        mock_search.return_value = [
            {"text": "Merge sort detail.", "filename": "ch5.pdf", "page": 2}
        ]

        mock_client.messages.create.side_effect = [
            _make_tool_response("t1", "search_pdfs", {"query": "merge sort"}),
            _make_tool_response("t2", "search_pdfs", {"query": "merge sort steps"}),
            _make_text_response("Merge sort works by dividing the array."),
        ]

        from app.agent.agent import run_agent

        _, sources = run_agent("Explain merge sort in detail.", "session-4")

        assert len(sources) == 1  # deduplicated
