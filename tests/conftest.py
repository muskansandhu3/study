"""
Pytest configuration for the test suite.

Integration tests (marked with @pytest.mark.integration) require a valid
Google AI Studio API key. They are automatically skipped only when the key
is missing or still set to an obvious placeholder value.
"""
import os
import pytest


def _has_configured_api_key() -> bool:
    """Check whether a non-placeholder Gemini API key is configured."""
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")
    normalized_key = key.strip()

    if not normalized_key:
        return False

    placeholder_values = {
        "your_gemini_api_key_here",
        "your_google_api_key_here",
        "your_api_key_here",
        "replace_me",
        "changeme",
    }

    lowered_key = normalized_key.lower()
    if lowered_key in placeholder_values:
        return False

    return not (lowered_key.startswith("your-") or lowered_key.startswith("your_"))


def pytest_collection_modifyitems(config, items):
    """Auto-skip integration tests when no configured API key is present."""
    if _has_configured_api_key():
        return

    skip_integration = pytest.mark.skip(
        reason=(
            "Integration test skipped: configure GEMINI_API_KEY or GOOGLE_API_KEY in .env. "
            "Google AI Studio keys may begin with AIzaSy or AQ."
        )
    )
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)
