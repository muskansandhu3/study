"""
Evaluation test cases for video moderation.
"""
import asyncio
from pydantic import BaseModel
from typing import List
from agents.video_agent import moderate_video


class VideoTestCase(BaseModel):
    """Test case for video moderation evaluation."""
    filename: str
    expected_contains_pii: bool
    expected_is_unfriendly: bool
    expected_is_unprofessional: bool
    description: str


# Define test cases
TEST_CASES: List[VideoTestCase] = [
    VideoTestCase(
        filename="product_demo.mp4",
        expected_contains_pii=False,
        expected_is_unfriendly=False,
        expected_is_unprofessional=False,
        description="Product demonstration video"
    ),
    VideoTestCase(
        filename="tutorial.mp4",
        expected_contains_pii=False,
        expected_is_unfriendly=False,
        expected_is_unprofessional=False,
        description="Tutorial video"
    ),
]


def create_test_video() -> bytes:
    """Create a minimal test video file."""
    # Minimal MP4 container
    return bytes([
        0x00, 0x00, 0x00, 0x20, 0x66, 0x74, 0x79, 0x70,
        0x69, 0x73, 0x6F, 0x6D, 0x00, 0x00, 0x02, 0x00
    ] * 8)


async def evaluate_case(test_case: VideoTestCase) -> dict:
    """Evaluate a single test case."""
    video_bytes = create_test_video()
    result = await moderate_video(video_bytes)
    
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
    print("VIDEO MODERATION EVALUATION")
    print("=" * 80)
    print()
    
    results = []
    for test_case in TEST_CASES:
        result = await evaluate_case(test_case)
        results.append(result)
    
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
        print()
        
        if result["all_correct"]:
            correct_count += 1
    
    accuracy = (correct_count / total_count) * 100
    print("=" * 80)
    print(f"SUMMARY: {correct_count}/{total_count} test cases passed ({accuracy:.1f}% accuracy)")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_evals())
