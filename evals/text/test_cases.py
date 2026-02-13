"""
Evaluation test cases for text moderation.
"""
import asyncio
from pydantic import BaseModel
from typing import List
from agents.text_agent import moderate_text
from moderation_types import ModerationResult


class TextTestCase(BaseModel):
    """Test case for text moderation evaluation."""
    text: str
    expected_contains_pii: bool
    expected_is_unfriendly: bool
    expected_is_unprofessional: bool
    description: str


# Define test cases
TEST_CASES: List[TextTestCase] = [
    # Clean, professional messages
    TextTestCase(
        text="Hello, I would like to inquire about your product offerings.",
        expected_contains_pii=False,
        expected_is_unfriendly=False,
        expected_is_unprofessional=False,
        description="Clean professional inquiry"
    ),
    TextTestCase(
        text="Thank you for your assistance. I appreciate your help.",
        expected_contains_pii=False,
        expected_is_unfriendly=False,
        expected_is_unprofessional=False,
        description="Polite thank you message"
    ),
    TextTestCase(
        text="Could you please provide more information about the warranty?",
        expected_contains_pii=False,
        expected_is_unfriendly=False,
        expected_is_unprofessional=False,
        description="Professional question"
    ),
    
    # PII cases
    TextTestCase(
        text="My email is john.doe@example.com and you can reach me there.",
        expected_contains_pii=True,
        expected_is_unfriendly=False,
        expected_is_unprofessional=False,
        description="Contains email address"
    ),
    TextTestCase(
        text="Please call me at 555-123-4567 to discuss further.",
        expected_contains_pii=True,
        expected_is_unfriendly=False,
        expected_is_unprofessional=False,
        description="Contains phone number"
    ),
    TextTestCase(
        text="My SSN is 123-45-6789 for verification.",
        expected_contains_pii=True,
        expected_is_unfriendly=False,
        expected_is_unprofessional=False,
        description="Contains Social Security Number"
    ),
    TextTestCase(
        text="I live at 123 Main Street, New York, NY 10001.",
        expected_contains_pii=True,
        expected_is_unfriendly=False,
        expected_is_unprofessional=False,
        description="Contains physical address"
    ),
    
    # Unfriendly cases
    TextTestCase(
        text="You are completely useless and this service is terrible!",
        expected_contains_pii=False,
        expected_is_unfriendly=True,
        expected_is_unprofessional=True,
        description="Hostile and insulting"
    ),
    TextTestCase(
        text="This is the worst experience I've ever had. You people are incompetent!",
        expected_contains_pii=False,
        expected_is_unfriendly=True,
        expected_is_unprofessional=True,
        description="Aggressive complaint"
    ),
    TextTestCase(
        text="I hate dealing with you idiots.",
        expected_contains_pii=False,
        expected_is_unfriendly=True,
        expected_is_unprofessional=True,
        description="Rude and insulting"
    ),
    
    # Unprofessional cases
    TextTestCase(
        text="I absolutely cannot offer you a damn refund for this crap.",
        expected_contains_pii=False,
        expected_is_unfriendly=True,
        expected_is_unprofessional=True,
        description="Profanity in refusal"
    ),
    TextTestCase(
        text="Whatever, just forget it. I don't care anymore.",
        expected_contains_pii=False,
        expected_is_unfriendly=False,
        expected_is_unprofessional=True,
        description="Dismissive and unprofessional"
    ),
    
    # Edge cases
    TextTestCase(
        text="I'm frustrated with this situation, but I understand you're trying to help.",
        expected_contains_pii=False,
        expected_is_unfriendly=False,
        expected_is_unprofessional=False,
        description="Expressing frustration professionally"
    ),
    TextTestCase(
        text="This product isn't working as expected. Can we find a solution?",
        expected_contains_pii=False,
        expected_is_unfriendly=False,
        expected_is_unprofessional=False,
        description="Complaint but professional"
    ),
]


async def evaluate_case(test_case: TextTestCase) -> dict:
    """Evaluate a single test case."""
    result = await moderate_text(test_case.text)
    
    # Check if predictions match expectations
    pii_correct = result.contains_pii == test_case.expected_contains_pii
    unfriendly_correct = result.is_unfriendly == test_case.expected_is_unfriendly
    unprofessional_correct = result.is_unprofessional == test_case.expected_is_unprofessional
    
    all_correct = pii_correct and unfriendly_correct and unprofessional_correct
    
    return {
        "description": test_case.description,
        "text": test_case.text[:60] + "..." if len(test_case.text) > 60 else test_case.text,
        "expected": {
            "pii": test_case.expected_contains_pii,
            "unfriendly": test_case.expected_is_unfriendly,
            "unprofessional": test_case.expected_is_unprofessional
        },
        "actual": {
            "pii": result.contains_pii,
            "unfriendly": result.is_unfriendly,
            "unprofessional": result.is_unprofessional
        },
        "correct": {
            "pii": pii_correct,
            "unfriendly": unfriendly_correct,
            "unprofessional": unprofessional_correct
        },
        "all_correct": all_correct,
        "rationale": result.rationale
    }


async def run_evals():
    """Run all evaluation cases."""
    print("=" * 80)
    print("TEXT MODERATION EVALUATION")
    print("=" * 80)
    print()
    
    results = []
    for test_case in TEST_CASES:
        result = await evaluate_case(test_case)
        results.append(result)
    
    # Print results
    correct_count = 0
    total_count = len(results)
    
    for i, result in enumerate(results, 1):
        status = "PASS" if result["all_correct"] else "FAIL"
        print(f"{i}. {status} - {result['description']}")
        print(f"   Text: {result['text']}")
        print(f"   Expected: PII={result['expected']['pii']}, "
              f"Unfriendly={result['expected']['unfriendly']}, "
              f"Unprofessional={result['expected']['unprofessional']}")
        print(f"   Actual:   PII={result['actual']['pii']}, "
              f"Unfriendly={result['actual']['unfriendly']}, "
              f"Unprofessional={result['actual']['unprofessional']}")
        
        if not result["all_correct"]:
            print(f"   Mismatches: ", end="")
            mismatches = []
            if not result["correct"]["pii"]:
                mismatches.append("PII")
            if not result["correct"]["unfriendly"]:
                mismatches.append("Unfriendly")
            if not result["correct"]["unprofessional"]:
                mismatches.append("Unprofessional")
            print(", ".join(mismatches))
        
        print()
        
        if result["all_correct"]:
            correct_count += 1
    
    # Summary
    accuracy = (correct_count / total_count) * 100
    print("=" * 80)
    print(f"SUMMARY: {correct_count}/{total_count} test cases passed ({accuracy:.1f}% accuracy)")
    print("=" * 80)
    print()
    print("Note: The text agent may not always achieve 100% accuracy.")
    print("This is expected behavior as LLM-based moderation has inherent variability.")


if __name__ == "__main__":
    asyncio.run(run_evals())
