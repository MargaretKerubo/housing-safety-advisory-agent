from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any


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
    
    @abstractmethod
    def generate_with_tools(
        self,
        contents: List[Dict],
        tools: List[Dict[str, Any]],
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """Generate content with function/tool calling support.
        
        Returns:
            Dict with 'type' ('text' or 'tool_calls') and corresponding data
        """
        pass
