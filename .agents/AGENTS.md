# Project Rules

## API Key / LLM Provider Preferences
- The primary LLM API key is Gemini (`GEMINI_API_KEY`).
- Wherever `OPENAI_API` or `OPENAI_API_KEY` is referenced, use Gemini's API as the primary implementation, but maintain OpenAI API (`OPENAI_API_KEY`) support as a fallback option for other developers.
