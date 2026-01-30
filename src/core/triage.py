
import json
from typing import List
from google import genai
from google.genai import types
from src.models.housing_models import HousingRequirements, Message


def triage_user_input(
    user_input: str,
    conversation_history: List[Message]
) -> HousingRequirements:
    """
    Analyzes user input to determine if we have all required information
    for housing recommendations.
    """
    from src.core.config import client  # Import here to avoid circular dependencies

    system_content = """You are an assistant that gathers key details for housing relocation in Kenya.

Extract the following from the conversation:
1. Current location (where they're moving from)
2. Target location (city/town they're moving to)
3. Workplace location (where they'll be working - e.g., "Kisumu CBD")
4. Monthly budget for rent (in KES)
5. Any preferences (security priorities, amenities, distance from work, etc.)

If all critical details are present (target location, workplace, and budget), return has_all_details: true.
If missing any critical info, return has_all_details: false.

Respond in JSON format matching this structure:
{
  "has_all_details": true,
  "current_location": "string or empty",
  "target_location": "string or empty",
  "workplace_location": "string or empty",
  "monthly_budget": 0,
  "preferences": "string or empty"
}

Return ONLY valid JSON, no markdown formatting."""

    # Build contents in the new format
    contents = [
        types.Content(
            role="user",
            parts=[types.Part(text=system_content)]
        )
    ]

    # Add conversation history
    for msg in conversation_history:
        contents.append(
            types.Content(
                role=msg["role"] if msg["role"] != "assistant" else "model",
                parts=[types.Part(text=msg["content"])]
            )
        )

    # Add current user input
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part(text=user_input)]
        )
    )

    response = client.models.generate_content(
        model="models/gemini-flash-latest",  # Updated model name
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=0.3,
            response_mime_type="application/json"
        ),
    )

    parsed = json.loads(response.text)
    return HousingRequirements(**parsed)