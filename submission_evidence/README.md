# Unit Test Evidence (for reviewer)

This folder contains raw terminal output files proving the requested unit tests were executed successfully.

## Environment
- Python: 3.11.15
- Runner available in this environment: `/Users/muskansandhu/Downloads/Gen/.venv/bin/python -m pytest`
- Note: `uv` was not installed in this runtime, so equivalent `python -m pytest` commands were used.

## Requested unit tests

Equivalent commands executed:

1. `python -m pytest tests/test_text_agent.py -vv`
   - Output: `submission_evidence/test_text_agent.txt`
   - Result: **4 passed**

2. `python -m pytest tests/test_image_agent.py -vv`
   - Output: `submission_evidence/test_image_agent.txt`
   - Result: **4 passed**

3. `python -m pytest tests/test_gradio_app.py -vv`
   - Output: `submission_evidence/test_gradio_app.txt`
   - Result: **9 passed**

4. `python -m pytest tests/test_moderation_result.py -vv`
   - Output: `submission_evidence/test_moderation_result.txt`
   - Result: **19 passed**

## Full test suite (additional evidence)

- Command: `python -m pytest tests/ -vv`
- Output: `submission_evidence/all_tests.txt`
- Result: **49 passed, 1 skipped**

The skipped test is a live integration API call and can be affected by external API key, model availability, or account billing/quota conditions.
