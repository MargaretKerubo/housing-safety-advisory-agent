import logging
from typing import List, Dict, Optional
from google import genai
from google.genai import types
from google.genai import errors as genai_errors
from .base import AIProvider
from app.utils.retry import retry_call, RetryableError

logger = logging.getLogger(__name__)

# Map Google Gen AI transient exceptions to our retryable wrapper
_GOOGLE_RETRYABLE = (
    genai_errors.ServerError,
    genai_errors.APIError,
)


class GeminiProvider(AIProvider):
    """Gemini AI provider implementation."""

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def _do_generate(self, model: str, contents: list, config) -> str:
        """Internal — performs the actual API call (target for retry)."""
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
            return response.text
        except _GOOGLE_RETRYABLE as e:
            raise RetryableError(str(e)) from e

    def generate_content(
        self,
        contents: List[Dict],
        temperature: float = 0.3,
        response_format: str = "json",
        max_tokens: Optional[int] = 1024,
    ) -> str:
        """Generate content using Gemini API with retry logic."""
        gemini_contents = []

        for msg in contents:
            role = "model" if msg["role"] == "assistant" else msg["role"]
            gemini_contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=msg["content"])]
                )
            )

        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            response_mime_type="application/json" if response_format == "json" else "text/plain"
        )

        return retry_call(
            self._do_generate,
            max_retries=3,
            base_delay=1.0,
            backoff=2.0,
            retryable_exceptions=(RetryableError,),
            model="models/gemini-flash-latest",
            contents=gemini_contents,
            config=config,
        )
