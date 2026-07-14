"""
Pytest configuration for the test suite.

Integration tests (marked with @pytest.mark.integration) require a valid
GEMINI_API_KEY. They are automatically skipped when the key appears to be
a placeholder or invalid format.
"""
import os
import pytest


def _has_valid_api_key() -> bool:
    """Check if GEMINI_API_KEY looks like a real Gemini API key."""
    key = os.environ.get("GEMINI_API_KEY", "")
    # Real Gemini API keys from AI Studio start with "AIzaSy"
    return key.startswith("AIzaSy") and len(key) >= 39


def pytest_collection_modifyitems(config, items):
    """Auto-skip integration tests when no valid API key is present."""
    if _has_valid_api_key():
        return  # Key looks valid, run all tests

    skip_integration = pytest.mark.skip(
        reason="Integration test skipped: GEMINI_API_KEY is not a valid Gemini API key. "
               "Get your key from https://aistudio.google.com/apikey (must start with AIzaSy)"
    )
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)
