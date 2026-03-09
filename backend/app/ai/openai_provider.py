from typing import List, Dict, Any
from openai import OpenAI
from .base import AIProvider
import json


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
        input_text = "\n\n".join([msg["content"] for msg in contents])
        
        response = self.client.responses.create(
            model="gpt-5-nano",
            input=input_text,
            store=True
        )
        
        return response.output_text
    
    def generate_with_tools(
        self,
        contents: List[Dict],
        tools: List[Dict[str, Any]],
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """Generate with function calling support."""
        messages = [{"role": msg["role"], "content": msg["content"]} for msg in contents]
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=[{"type": "function", "function": tool} for tool in tools],
            temperature=temperature
        )
        
        message = response.choices[0].message
        
        if message.tool_calls:
            return {
                "type": "tool_calls",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "name": tc.function.name,
                        "arguments": json.loads(tc.function.arguments)
                    }
                    for tc in message.tool_calls
                ]
            }
        else:
            return {
                "type": "text",
                "content": message.content
            }
