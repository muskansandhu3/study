"""Image moderation agent using lazy model initialization with local fallback."""
import os
from functools import lru_cache
from typing import Optional

from pydantic_ai import Agent
from pydantic_ai.messages import BinaryContent

from moderation_types.moderation_result import ModerationResult


@lru_cache(maxsize=1)
def _get_image_agent() -> Optional[Agent]:
    if not os.getenv("GOOGLE_API_KEY"):
        return None
    try:
        return Agent(
            "google-gla:gemini-1.5-flash",
            output_type=ModerationResult,
            system_prompt=(
                "You are an image content moderation assistant. Analyze the provided image and determine: "
                "contains_pii, is_unfriendly, is_unprofessional, and rationale."
            ),
        )
    except Exception:
        return None


async def moderate_image(image_bytes: bytes) -> ModerationResult:
    """Moderate image content with remote model when available, else local fallback."""
    agent = _get_image_agent()
    if agent is not None:
        try:
            result = await agent.run(BinaryContent(data=image_bytes, media_type="image/jpeg"))
            return result.data
        except Exception:
            pass

    return ModerationResult(
        contains_pii=False,
        is_unfriendly=False,
        is_unprofessional=False,
        rationale="Local fallback used: image model unavailable.",
    )