import pytest
from moderation_types.moderation_result import ModerationResult


def test_moderation_result_defaults():
    result = ModerationResult()
    assert result.contains_pii is False
    assert result.is_unfriendly is False
    assert result.is_unprofessional is False
    assert result.rationale == ""


def test_is_flagged():
    result1 = ModerationResult()
    assert result1.is_flagged() is False
    
    result2 = ModerationResult(contains_pii=True)
    assert result2.is_flagged() is True
