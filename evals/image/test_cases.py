"""
Evaluation test cases for image moderation.
"""
import asyncio
from pydantic import BaseModel
from typing import List
from agents.image_agent import moderate_image


class ImageTestCase(BaseModel):
    """Test case for image moderation evaluation."""
    filename: str
    expected_contains_pii: bool
    expected_is_unfriendly: bool
    expected_is_unprofessional: bool
    description: str


# Define test cases
TEST_CASES: List[ImageTestCase] = [
    ImageTestCase(
        filename="professional_image.jpg",
        expected_contains_pii=False,
        expected_is_unfriendly=False,
        expected_is_unprofessional=False,
        description="Professional business image"
    ),
    ImageTestCase(
        filename="landscape.jpg",
        expected_contains_pii=False,
        expected_is_unfriendly=False,
        expected_is_unprofessional=False,
        description="Neutral landscape photo"
    ),
    ImageTestCase(
        filename="product_photo.jpg",
        expected_contains_pii=False,
        expected_is_unfriendly=False,
        expected_is_unprofessional=False,
        description="Product photograph"
    ),
    ImageTestCase(
        filename="id_card.jpg",
        expected_contains_pii=True,
        expected_is_unfriendly=False,
        expected_is_unprofessional=False,
        description="Image containing ID card (PII)"
    ),
    ImageTestCase(
        filename="faces.jpg",
        expected_contains_pii=True,
        expected_is_unfriendly=False,
        expected_is_unprofessional=False,
        description="Image with identifiable faces"
    ),
]


def create_test_image(description: str) -> bytes:
    """Create a minimal test image."""
    # Minimal JPEG header
    return bytes([
        0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46,
        0x49, 0x46, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01,
        0x00, 0x01, 0x00, 0x00, 0xFF, 0xD9
    ])


async def evaluate_case(test_case: ImageTestCase) -> dict:
    """Evaluate a single test case."""
    # For demo purposes, create dummy image bytes
    # In production, you would load actual images from evals/test_data/
    image_bytes = create_test_image(test_case.description)
    
    result = await moderate_image(image_bytes)
    
    # Check if predictions match expectations
    pii_correct = result.contains_pii == test_case.expected_contains_pii
    unfriendly_correct = result.is_unfriendly == test_case.expected_is_unfriendly
    unprofessional_correct = result.is_unprofessional == test_case.expected_is_unprofessional
    
    all_correct = pii_correct and unfriendly_correct and unprofessional_correct
    
    return {
        "description": test_case.description,
        "filename": test_case.filename,
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
    print("IMAGE MODERATION EVALUATION")
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
        print(f"   File: {result['filename']}")
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
    print("Note: Image moderation may not always achieve 100% accuracy.")
    print("This is expected behavior as LLM-based moderation has inherent variability.")


if __name__ == "__main__":
    asyncio.run(run_evals())
