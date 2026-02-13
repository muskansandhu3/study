from pydantic import BaseModel, Field


class ModerationResult(BaseModel):
    contains_pii: bool = Field(default=False)
    is_unfriendly: bool = Field(default=False)
    is_unprofessional: bool = Field(default=False)
    rationale: str = Field(default="")
    
    def is_flagged(self) -> bool:
        return self.contains_pii or self.is_unfriendly or self.is_unprofessional
