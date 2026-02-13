"""
Tests for audio moderation agent.
"""
import pytest
import asyncio
from agents.audio_agent import moderate_audio
from moderation_types import ModerationResult


def create_dummy_audio_bytes() -> bytes:
    """Create minimal valid WAV bytes for testing."""
    # Minimal WAV header
    return bytes([
        0x52, 0x49, 0x46, 0x46,  # "RIFF"
        0x24, 0x00, 0x00, 0x00,  # Chunk size
        0x57, 0x41, 0x56, 0x45,  # "WAVE"
        0x66, 0x6D, 0x74, 0x20   # "fmt "
    ] * 4)


@pytest.mark.asyncio
async def test_moderate_audio_returns_result():
    """Test that audio moderation returns a ModerationResult."""
    audio_bytes = create_dummy_audio_bytes()
    result = await moderate_audio(audio_bytes)
    
    assert isinstance(result, ModerationResult)


@pytest.mark.asyncio
async def test_moderate_audio_has_rationale():
    """Test that audio moderation includes a rationale."""
    audio_bytes = create_dummy_audio_bytes()
    result = await moderate_audio(audio_bytes)
    
    assert isinstance(result.rationale, str)


@pytest.mark.asyncio
async def test_moderate_audio_fields():
    """Test that all expected fields are present."""
    audio_bytes = create_dummy_audio_bytes()
    result = await moderate_audio(audio_bytes)
    
    assert hasattr(result, 'contains_pii')
    assert hasattr(result, 'is_unfriendly')
    assert hasattr(result, 'is_unprofessional')
    assert hasattr(result, 'rationale')


def test_moderate_audio_sync():
    """Synchronous test wrapper."""
    audio_bytes = create_dummy_audio_bytes()
    result = asyncio.run(moderate_audio(audio_bytes))
    assert isinstance(result, ModerationResult)


if __name__ == "__main__":
    pytest.main([__file__, "-vv"])
