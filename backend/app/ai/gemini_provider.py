from typing import List, Dict, Any
from google import genai
from google.genai import types
from .base import AIProvider
import json


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
    
    def generate_with_tools(
        self,
        contents: List[Dict],
        tools: List[Dict[str, Any]],
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """Generate with function calling support."""
        gemini_contents = []
        
        for msg in contents:
            role = "model" if msg["role"] == "assistant" else msg["role"]
            gemini_contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=msg["content"])]
                )
            )
        
        # Convert tools to Gemini format
        gemini_tools = [types.Tool(function_declarations=[
            types.FunctionDeclaration(
                name=tool["name"],
                description=tool["description"],
                parameters=tool["parameters"]
            ) for tool in tools
        ])]
        
        response = self.client.models.generate_content(
            model="models/gemini-2.0-flash-exp",
            contents=gemini_contents,
            config=types.GenerateContentConfig(
                temperature=temperature,
                tools=gemini_tools
            )
        )
        
        # Check if response has function calls
        if response.candidates[0].content.parts[0].function_call:
            fc = response.candidates[0].content.parts[0].function_call
            return {
                "type": "tool_calls",
                "tool_calls": [{
                    "id": "gemini_call",
                    "name": fc.name,
                    "arguments": dict(fc.args)
                }]
            }
        else:
            return {
                "type": "text",
                "content": response.text
            }
