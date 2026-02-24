from abc import ABC, abstractmethod
from typing import List, Dict


class AIProvider(ABC):
    """Abstract base class for AI provider implementations."""
    
    @abstractmethod
    def generate_content(
        self,
        contents: List[Dict],
        temperature: float = 0.3,
        response_format: str = "json"
    ) -> str:
        """Generate content based on conversation history."""
        pass
