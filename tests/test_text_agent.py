import pytest
import asyncio
from agents.text_agent import moderate_text


@pytest.mark.asyncio
async def test_moderate_clean_text():
    text = "Hello, how can I help you?"
    result = await moderate_text(text)
    assert result is not None
    assert hasattr(result, 'contains_pii')


def test_sync_wrapper():
    text = "Hello"
    result = asyncio.run(moderate_text(text))
    assert result is not None
