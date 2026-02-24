
from typing import List
from src.models.housing_models import HousingRequirements, Message


def gather_missing_details(
    requirements: HousingRequirements,
    conversation_history: List[Message]
) -> str:
    """
    Asks user for missing information in a friendly way.
    """
    from src.core.config import ai_provider
    
    missing_items = []

    if not requirements.target_location:
        missing_items.append("target location (which city/town)")
    if not requirements.workplace_location:
        missing_items.append("workplace location")
    if not requirements.monthly_budget or requirements.monthly_budget == 0:
        missing_items.append("monthly budget for rent")

    if not missing_items:
        return "It seems we have all the necessary information. Is there anything else you'd like to add?"

    prompt = f"""You are a friendly housing assistant helping someone relocate in Kenya.

The user is missing these details: {', '.join(missing_items)}

Ask for the missing information in a conversational, friendly way. Don't overwhelm them - ask naturally.
Keep your response concise (2-3 sentences max)."""

    response_text = ai_provider.generate_content(
        contents=[{"role": "user", "content": prompt}],
        temperature=0.7,
        response_format="text"
    )

    return response_text or "Could you provide more details about your relocation?"