from functools import lru_cache
from app.config import settings

class GeminiService:
    def __init__(self):
        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. Add it to .env before using AI generation."
            )
        try:
            from google import genai
        except ImportError as exc:
            raise RuntimeError(
                "The Google Gen AI SDK is missing. Run: pip install -r requirements.txt"
            ) from exc

        self.client = genai.Client(api_key=settings.gemini_api_key)

    def generate(self, model: str, prompt: str, *, temperature: float = 0.7, max_tokens: int = 3000) -> str:
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )
        except Exception as exc:
            raise RuntimeError(f"Gemini API request failed: {exc}") from exc

        text = getattr(response, "text", None)
        if not text:
            raise RuntimeError("Gemini returned an empty response.")
        return text.strip()

@lru_cache
def get_gemini_service() -> GeminiService:
    return GeminiService()
