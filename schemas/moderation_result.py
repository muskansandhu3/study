"""
Pydantic model for moderation results.
"""
from pydantic import BaseModel, Field


class ModerationResult(BaseModel):
    """
    Structured output model for content moderation.
    
    Attributes:
        contains_pii: Whether the content contains personally identifiable information
        is_unfriendly: Whether the content is unfriendly or hostile
        is_unprofessional: Whether the content is unprofessional
        rationale: Explanation for the moderation decision
    """
    contains_pii: bool = Field(
        default=False,
        description="Whether the content contains personally identifiable information (PII) such as email, phone, SSN, address"
    )
    is_unfriendly: bool = Field(
        default=False,
        description="Whether the content is unfriendly, hostile, or rude"
    )
    is_unprofessional: bool = Field(
        default=False,
        description="Whether the content is unprofessional or inappropriate for a business context"
    )
    rationale: str = Field(
        default="",
        description="Detailed explanation for the moderation decision"
    )
    
    def is_flagged(self) -> bool:
        """Check if any moderation flag is raised."""
        return self.contains_pii or self.is_unfriendly or self.is_unprofessional
