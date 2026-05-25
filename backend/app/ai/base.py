from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class AIProvider(ABC):
    """Abstract base class for AI provider implementations."""

    @abstractmethod
    def generate_content(
        self,
        contents: List[Dict],
        temperature: float = 0.3,
        response_format: str = "json",
        max_tokens: Optional[int] = 1024,
    ) -> str:
        """Generate content based on conversation history."""
        pass
