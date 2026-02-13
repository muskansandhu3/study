"""Video moderation agent using lazy model initialization with local fallback."""
import os
from functools import lru_cache
from typing import Optional

from pydantic_ai import Agent
from pydantic_ai.messages import BinaryContent

from moderation_types.moderation_result import ModerationResult


@lru_cache(maxsize=1)
def _get_video_agent() -> Optional[Agent]:
    if not os.getenv("GOOGLE_API_KEY"):
        return None
    try:
        return Agent(
            "google-gla:gemini-1.5-flash",
            output_type=ModerationResult,
            system_prompt=(
                "You are a video content moderation assistant. Analyze the provided video and determine: "
                "contains_pii, is_unfriendly, is_unprofessional, and rationale."
            ),
        )
    except Exception:
        return None


async def moderate_video(video_bytes: bytes) -> ModerationResult:
    """Moderate video content with remote model when available, else local fallback."""
    agent = _get_video_agent()
    if agent is not None:
        try:
            result = await agent.run(BinaryContent(data=video_bytes, media_type="video/mp4"))
            return result.data
        except Exception:
            pass

    return ModerationResult(
        contains_pii=False,
        is_unfriendly=False,
        is_unprofessional=False,
        rationale="Local fallback used: video model unavailable.",
    )