"""
Tests for image moderation agent.
"""
import pytest
import asyncio
from pathlib import Path
from agents.image_agent import moderate_image
from moderation_types import ModerationResult


def create_dummy_image_bytes() -> bytes:
    """Create minimal valid JPEG bytes for testing."""
    # Minimal JPEG header
    return bytes([
        0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46,
        0x49, 0x46, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01,
        0x00, 0x01, 0x00, 0x00, 0xFF, 0xD9
    ])


@pytest.mark.asyncio
async def test_moderate_image_returns_result():
    """Test that image moderation returns a ModerationResult."""
    image_bytes = create_dummy_image_bytes()
    result = await moderate_image(image_bytes)
    
    assert isinstance(result, ModerationResult)


@pytest.mark.asyncio
async def test_moderate_image_has_rationale():
    """Test that image moderation includes a rationale."""
    image_bytes = create_dummy_image_bytes()
    result = await moderate_image(image_bytes)
    
    assert isinstance(result.rationale, str)


@pytest.mark.asyncio
async def test_moderate_image_fields():
    """Test that all expected fields are present."""
    image_bytes = create_dummy_image_bytes()
    result = await moderate_image(image_bytes)
    
    assert hasattr(result, 'contains_pii')
    assert hasattr(result, 'is_unfriendly')
    assert hasattr(result, 'is_unprofessional')
    assert hasattr(result, 'rationale')


def test_moderate_image_sync():
    """Synchronous test wrapper."""
    image_bytes = create_dummy_image_bytes()
    result = asyncio.run(moderate_image(image_bytes))
    assert isinstance(result, ModerationResult)


if __name__ == "__main__":
    pytest.main([__file__, "-vv"])
