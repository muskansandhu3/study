"""
Tests for Gradio app functionality.
"""
import pytest
import asyncio
from gradio_app import moderate_content, chat_function


@pytest.mark.asyncio
async def test_moderate_clean_content():
    """Test moderation of clean content."""
    is_flagged, reason = await moderate_content(
        "Hello, how can I help you today?",
        files=None,
        session_id="test-session"
    )
    
    assert is_flagged is False
    assert reason == ""


@pytest.mark.asyncio
async def test_moderate_flagged_content():
    """Test moderation of flagged content."""
    is_flagged, reason = await moderate_content(
        "You are absolutely useless and terrible!",
        files=None,
        session_id="test-session"
    )
    
    assert is_flagged is True
    assert len(reason) > 0


@pytest.mark.asyncio
async def test_chat_function_basic():
    """Test basic chat function."""
    message = {"text": "Hello, I need help", "files": []}
    history = []
    
    result = await chat_function(message, history, session_id="test-session")
    
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_chat_function_with_flag():
    """Test chat function with flagged content."""
    message = {"text": "This service is completely useless!", "files": []}
    history = []
    
    result = await chat_function(message, history, session_id="test-session")
    
    assert isinstance(result, list)
    assert len(result) > 0
    # Should contain warning message
    assert any("Moderation Alert" in str(item) for item in result)


def test_moderate_content_sync():
    """Synchronous test wrapper."""
    is_flagged, reason = asyncio.run(
        moderate_content("Test message", None, "test-session")
    )
    assert isinstance(is_flagged, bool)
    assert isinstance(reason, str)


if __name__ == "__main__":
    pytest.main([__file__, "-vv"])
