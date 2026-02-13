"""Customer response agent with lazy remote model and local fallback."""
import os
from functools import lru_cache
from typing import Optional

from pydantic_ai import Agent


@lru_cache(maxsize=1)
def _get_customer_backend() -> Optional[Agent]:
    if not os.getenv("GOOGLE_API_KEY"):
        return None
    try:
        return Agent(
            "google-gla:gemini-1.5-flash",
            output_type=str,
            system_prompt=(
                "You are a customer interacting with customer service. "
                "Keep responses concise and realistic. "
                "Respond in English only."
            ),
        )
    except Exception:
        return None


class CustomerAgent:
    """Light wrapper exposing a stable async run interface."""

    async def run(self, conversation_history: str) -> str:
        backend = _get_customer_backend()
        if backend is not None:
            try:
                result = await backend.run(conversation_history)
                return result.data
            except Exception:
                pass

        history = conversation_history or ""
        lower = history.lower()

        # Deterministic fallback persona with simple context branching.
        # This chatbot simulates the customer side, not the support agent.
        positive_cues = (
            "help", "solution", "replace", "replacement", "refund", "next steps",
        )
        negative_cues = (
            "can't", "cannot", "no refund", "impossible", "policy", "denied",
        )
        greeting_cues = ("hello", "hi", "hey", "good morning", "good evening")

        cooperative_replies = [
            "Thanks for helping. Can you confirm the exact next steps?",
            "I appreciate the support. Please tell me what happens next.",
            "Okay, that sounds fair. What do I need to do now?",
        ]
        frustrated_replies = [
            "I'm still frustrated about this issue and need a clear resolution.",
            "This has taken too long and I need a concrete fix today.",
            "I understand, but this is still unresolved and very frustrating.",
        ]
        escalation_replies = [
            "This is unacceptable. Please escalate me to a supervisor.",
            "If this cannot be fixed now, I want this escalated immediately.",
            "This response is not enough. I need a manager to review my case.",
        ]
        opening_replies = [
            "Hi. I'm contacting support because my product is not working and I need help.",
            "Hello. I have a problem with my order and I need a resolution.",
            "Hi there. I'm frustrated because this issue is still unresolved.",
        ]

        def pick(options: list[str]) -> str:
            # Stable variation based on conversation text.
            return options[abs(hash(lower)) % len(options)]

        if any(cue in lower for cue in greeting_cues):
            return pick(opening_replies)
        if any(cue in lower for cue in negative_cues):
            return pick(escalation_replies)
        if any(cue in lower for cue in positive_cues):
            return pick(cooperative_replies)
        return pick(frustrated_replies)


customer_agent = CustomerAgent()


async def run(conversation_history: str) -> str:
    """Backward-compatible module-level helper."""
    return await customer_agent.run(conversation_history)
