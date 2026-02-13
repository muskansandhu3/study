"""Text moderation agent with lazy model initialization and local fallback."""
import os
import re
from functools import lru_cache
from typing import Optional

from pydantic_ai import Agent

from moderation_types.moderation_result import ModerationResult


@lru_cache(maxsize=1)
def _get_text_agent() -> Optional[Agent]:
    """Create the remote text moderation agent only when an API key is available."""
    if not os.getenv("GOOGLE_API_KEY"):
        return None
    try:
        return Agent(
            "google-gla:gemini-flash-latest",
            output_type=ModerationResult,
            system_prompt=(
                "Analyze text for: 1) PII (email, phone, SSN), "
                "2) unfriendly tone, 3) unprofessional language. "
                "Return structured result."
            ),
        )
    except Exception:
        return None


def _rule_based_text_moderation(text: str) -> ModerationResult:
    """Deterministic fallback moderation for local runs and tests."""
    value = text or ""
    lower = value.lower()

    contains_email = bool(re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", value))
    contains_phone = bool(re.search(r"\b(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}\b", value))
    contains_pii = contains_email or contains_phone

    unfriendly_terms = (
        # English
        "useless", "terrible", "idiot", "stupid", "hate", "worst", "moron",
        "loser", "trash", "garbage", "dickhead",
        # Spanish
        "idiota", "inutil", "estupido", "estupida", "imbecil", "gilipollas",
        "cabron", "basura", "odio",
        # Italian
        "coglione", "cogliona", "stronzo", "stronza", "idiota", "inutile",
        "stupido", "stupida", "odio",
    )
    unprofessional_terms = (
        # English
        "fuck", "shit", "damn", "bitch", "asshole", "bastard",
        "motherfucker", "fucking",
        # Spanish
        "mierda", "joder", "cojones", "puta", "puto", "hijo de puta",
        "pendejo", "pendeja",
        # Italian
        "cazzo", "merda", "vaffanculo", "troia", "puttana",
    )

    is_unfriendly = any(term in lower for term in unfriendly_terms)
    is_unprofessional = any(term in lower for term in unprofessional_terms)

    if contains_pii or is_unfriendly or is_unprofessional:
        reasons = []
        if contains_pii:
            reasons.append("possible PII detected")
        if is_unfriendly:
            reasons.append("unfriendly tone detected")
        if is_unprofessional:
            reasons.append("unprofessional language detected")
        rationale = "; ".join(reasons)
    else:
        rationale = "No obvious moderation issues detected."

    return ModerationResult(
        contains_pii=contains_pii,
        is_unfriendly=is_unfriendly,
        is_unprofessional=is_unprofessional,
        rationale=rationale,
    )


async def moderate_text(text: str) -> ModerationResult:
    """Moderate text content with remote model when available, else local fallback."""
    agent = _get_text_agent()
    if agent is not None:
        try:
            result = await agent.run(text)
            return result.data
        except Exception:
            pass

    return _rule_based_text_moderation(text)
