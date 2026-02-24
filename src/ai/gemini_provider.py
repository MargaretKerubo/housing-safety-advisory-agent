from typing import List, Dict
from google import genai
from google.genai import types
from .base import AIProvider


class GeminiProvider(AIProvider):
    """Gemini AI provider implementation."""
    
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
    
    def generate_content(
        self,
        contents: List[Dict],
        temperature: float = 0.3,
        response_format: str = "json"
    ) -> str:
        """Generate content using Gemini API."""
        gemini_contents = []
        
        for msg in contents:
            role = "model" if msg["role"] == "assistant" else msg["role"]
            gemini_contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=msg["content"])]
                )
            )
        
        response = self.client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=gemini_contents,
            config=types.GenerateContentConfig(
                temperature=temperature,
                response_mime_type="application/json" if response_format == "json" else "text/plain"
            ),
        )
        
        return response.text
