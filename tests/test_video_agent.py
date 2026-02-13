"""
Tests for video moderation agent.
"""
import pytest
import asyncio
from agents.video_agent import moderate_video
from moderation_types import ModerationResult


def create_dummy_video_bytes() -> bytes:
    """Create minimal valid MP4 bytes for testing."""
    # Minimal MP4 container with ftyp box
    return bytes([
        0x00, 0x00, 0x00, 0x20, 0x66, 0x74, 0x79, 0x70,
        0x69, 0x73, 0x6F, 0x6D, 0x00, 0x00, 0x02, 0x00
    ] * 4)


@pytest.mark.asyncio
async def test_moderate_video_returns_result():
    """Test that video moderation returns a ModerationResult."""
    video_bytes = create_dummy_video_bytes()
    result = await moderate_video(video_bytes)
    
    assert isinstance(result, ModerationResult)


@pytest.mark.asyncio
async def test_moderate_video_has_rationale():
    """Test that video moderation includes a rationale."""
    video_bytes = create_dummy_video_bytes()
    result = await moderate_video(video_bytes)
    
    assert isinstance(result.rationale, str)


@pytest.mark.asyncio
async def test_moderate_video_fields():
    """Test that all expected fields are present."""
    video_bytes = create_dummy_video_bytes()
    result = await moderate_video(video_bytes)
    
    assert hasattr(result, 'contains_pii')
    assert hasattr(result, 'is_unfriendly')
    assert hasattr(result, 'is_unprofessional')
    assert hasattr(result, 'rationale')


def test_moderate_video_sync():
    """Synchronous test wrapper."""
    video_bytes = create_dummy_video_bytes()
    result = asyncio.run(moderate_video(video_bytes))
    assert isinstance(result, ModerationResult)


if __name__ == "__main__":
    pytest.main([__file__, "-vv"])
