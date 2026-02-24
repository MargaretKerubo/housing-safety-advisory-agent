from typing import List, Dict
from openai import OpenAI
from .base import AIProvider


class OpenAIProvider(AIProvider):
    """OpenAI provider implementation."""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def generate_content(
        self,
        contents: List[Dict],
        temperature: float = 0.3,
        response_format: str = "json"
    ) -> str:
        """Generate content using OpenAI API."""
        # Combine all messages into a single input
        input_text = "\n\n".join([msg["content"] for msg in contents])
        
        response = self.client.responses.create(
            model="gpt-5-nano",
            input=input_text,
            store=True
        )
        
        return response.output_text
