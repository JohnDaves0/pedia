import os
import pytest

# Provide a dummy API key so config loads without a real .env during tests
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
