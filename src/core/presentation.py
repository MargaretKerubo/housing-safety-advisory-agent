

from typing import List
from src.models.housing_models import NeighborhoodRecommendation, HousingRequirements, Message


def present_recommendations(
    recommendations: NeighborhoodRecommendation,
    requirements: HousingRequirements,
    conversation_history: List[Message]
) -> str:
    """
    Formats and presents recommendations in a user-friendly way.
    """
    from src.core.config import ai_provider

    prompt = f"""You are a helpful housing assistant presenting neighborhood recommendations.

Create a clear, friendly summary that includes:
1. Brief introduction acknowledging their move to {requirements.target_location}
2. Each neighborhood recommendation with:
   - Name and location
   - Rent range
   - Security highlights (emphasize this - it's important!)
   - Distance/commute to {requirements.workplace_location}
   - Key amenities
   - Notable pros and cons
3. Practical next steps (viewing properties, contacting agents, verification tips)

Use clear formatting with headers and bullet points. Be encouraging and helpful.
Keep it conversational but informative.

Target city: {requirements.target_location}
Workplace: {requirements.workplace_location}

Recommendations JSON:
{recommendations.model_dump_json()}"""

    response_text = ai_provider.generate_content(
        contents=[{"role": "user", "content": prompt}],
        temperature=0.7,
        response_format="text"
    )

    return response_text or "Here are your recommendations."