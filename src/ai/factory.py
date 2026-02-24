import os
from .base import AIProvider
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider


def get_ai_provider() -> AIProvider:
    """Factory function to get the configured AI provider."""
    provider_type = os.getenv("AI_PROVIDER", "gemini").lower()
    
    if provider_type == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        return OpenAIProvider(api_key)
    elif provider_type == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        return GeminiProvider(api_key)
    else:
        raise ValueError(f"Unknown AI provider: {provider_type}")
