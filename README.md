# Multimodal Moderation

This project uses Google Gemini models for multimodal moderation.

## API key formats

Google AI Studio currently issues Gemini API keys in multiple formats. This project supports both of these key prefixes:

- `AIzaSy...`
- `AQ....`

The application does not enforce a specific key prefix. It passes the configured key directly to the Google provider and lets the Gemini API determine whether the key is valid.

## Environment setup

Create a `.env` file in the project root. You can use either `GEMINI_API_KEY` or `GOOGLE_API_KEY`.

Example:

```dotenv
GEMINI_API_KEY=AQ.your_google_ai_studio_key_here
USER_API_KEY=your_user_api_key_here
DEFAULT_GOOGLE_MODEL=gemini-2.5-flash
```

## Notes

- Keys created in Google AI Studio may start with either `AQ.` or `AIzaSy`.
- Authentication is delegated to the configured Google provider / Google GenAI SDK path without any hard-coded prefix validation.
- Integration tests run when a non-placeholder API key is configured.