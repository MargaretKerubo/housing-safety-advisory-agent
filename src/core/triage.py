
import json
from typing import List
from src.models.housing_models import HousingRequirements, Message


def triage_user_input(
    user_input: str,
    conversation_history: List[Message]
) -> HousingRequirements:
    """
    Analyzes user input to determine if we have all required information
    for housing recommendations.
    """
    from src.core.config import ai_provider

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

    # Build contents
    contents = [{"role": "user", "content": system_content}]
    
    for msg in conversation_history:
        contents.append({"role": msg["role"], "content": msg["content"]})
    
    contents.append({"role": "user", "content": user_input})

    response_text = ai_provider.generate_content(
        contents=contents,
        temperature=0.3,
        response_format="json"
    )

    parsed = json.loads(response_text)
    return HousingRequirements(**parsed)