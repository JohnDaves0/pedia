TOOLS = [
    {
        "name": "search_pdfs",
        "description": (
            "Search through the PDF course materials to find relevant content. "
            "Use this when the user asks about topics, algorithms, definitions, examples, "
            "or exercises that would appear in the documents."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A concise search query describing what to look for.",
                }
            },
            "required": ["query"],
        },
    }
]
