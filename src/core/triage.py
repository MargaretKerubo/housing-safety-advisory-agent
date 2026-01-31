
import json
from typing import List, Optional
from google import genai
from google.genai import types
from src.models.housing_models import HousingRequirements, Message
from src.core.safety_guardrails import validate_query, inject_safety_context


def triage_user_input(
    user_input: str,
    conversation_history: List[Message]
) -> tuple[HousingRequirements, Optional[str], Optional[str]]:
    """
    Analyzes user input to determine if we have all required information
    for housing recommendations.
    
    Returns:
        tuple of (HousingRequirements, warning_message, advisory_disclaimer)
        warning_message and advisory_disclaimer will be None if query is safe
    """
    from src.core.config import client  # Import here to avoid circular dependencies

    # Apply safety guardrails first
    guardrail_result = validate_query(user_input)
    
    # Use reframed query if original was problematic
    processed_input = guardrail_result.reframed_query or user_input

    system_content = """You are an assistant that gathers key details for housing relocation in Kenya.

Extract the following from the conversation:
1. Current location (where they're moving from)
2. Target location (city/town they're moving to)
3. Workplace location (where they'll be working - e.g., "Kisumu CBD")
4. Monthly budget for rent (in KES)
5. Any preferences (amenities, distance from work, transportation, etc.)

IMPORTANT: Focus on OBJECTIVE preferences like budget, commute, and amenities.
Do NOT extract or perpetuate stereotypes about areas being "dangerous" or "unsafe".
If user mentions area stereotypes, ignore them and focus on factual criteria.

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

    # Add current user input (using processed input if stereotypes were detected)
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part(text=processed_input)]
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
    requirements = HousingRequirements(**parsed)
    
    # Return requirements along with any guardrail warnings
    return (
        requirements,
        guardrail_result.warning_message,
        guardrail_result.advisory_disclaimer
    )
