from .base import AIProvider
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider
from app.config import Config


def get_ai_provider() -> AIProvider:
    if Config.AI_PROVIDER == "openai":
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment")
        return OpenAIProvider(Config.OPENAI_API_KEY)
    elif Config.AI_PROVIDER == "gemini":
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment")
        return GeminiProvider(Config.GEMINI_API_KEY)
    else:
        raise ValueError(f"Unknown AI provider: {Config.AI_PROVIDER}")
