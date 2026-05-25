import logging
from typing import List, Dict, Optional
from openai import OpenAI
from openai import APIError, APITimeoutError, RateLimitError, APIConnectionError
from .base import AIProvider
from app.utils.retry import retry_call, RetryableError

logger = logging.getLogger(__name__)

# Map OpenAI transient exceptions to our retryable wrapper
_OPENAI_RETRYABLE = (
    APITimeoutError,
    RateLimitError,
    APIConnectionError,
    APIError,
)


class OpenAIProvider(AIProvider):
    """OpenAI provider implementation."""

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def _do_generate(
        self,
        messages: list,
        temperature: float,
        max_tokens: int,
        response_format: dict,
    ) -> str:
        """Internal — performs the actual API call (target for retry)."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format,
            )
            return response.choices[0].message.content
        except _OPENAI_RETRYABLE as e:
            raise RetryableError(str(e)) from e

    def generate_content(
        self,
        contents: List[Dict],
        temperature: float = 0.3,
        response_format: str = "json",
        max_tokens: Optional[int] = 1024,
    ) -> str:
        """Generate content using OpenAI API with retry logic."""
        messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in contents
        ]

        fmt = {"type": "json_object"} if response_format == "json" else {"type": "text"}

        return retry_call(
            self._do_generate,
            max_retries=3,
            base_delay=1.0,
            backoff=2.0,
            retryable_exceptions=(RetryableError,),
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=fmt,
        )
