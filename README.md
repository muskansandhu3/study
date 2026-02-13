# Multimodal Content Moderation System

AI-powered moderation for text, images, audio, and video using Pydantic AI and Google Gemini.

## Requirements

- Python 3.10+
- Google AI Studio API key (`GOOGLE_API_KEY`)

Get your API key: https://aistudio.google.com/app/apikey

## Setup

### Option A: UV (Recommended)

```bash
uv sync
```

### Option B: pip

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment Configuration

Create `.env` from `.env.example` and set at least:

```env
GOOGLE_API_KEY=your_actual_api_key_here
GRADIO_SERVER_PORT=7860
GRADIO_SERVER_NAME=0.0.0.0
PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6006/v1/traces
```


## Run Tests

```bash
uv run pytest tests/ -vv
```

## Run Evals

```bash
uv run evals/text/test_cases.py
uv run evals/image/test_cases.py
uv run evals/audio/test_cases.py
uv run evals/video/test_cases.py
```

Mixed pass/fail in evals is expected for LLM-based moderation.

## Run the App

```bash
uv run multimodal-moderation
```

Open: `http://localhost:7860`

If the port is busy, set another one:

```bash
# PowerShell example
$env:GRADIO_SERVER_PORT="7900"
uv run multimodal-moderation
```

## Optional: Phoenix Observability

In a separate terminal:

```bash
pip install arize-phoenix
python -m phoenix.server.main serve
```

Open Phoenix UI: `http://localhost:6006/projects`

Look for spans such as:

- `conversation`
- `chat_turn`
- `moderate_text`
- `feedback`

## Project Structure

- `agents/` - Moderation agents (text, image, audio, video, customer)
- `moderation_types/` - Pydantic models
- `tests/` - Unit tests
- `evals/` - Evaluation test cases
- `gradio_app.py` - Chat UI
- `tracing.py` - OpenTelemetry setup
