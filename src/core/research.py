
import json
from typing import List
from google import genai
from google.genai import types
from src.models.housing_models import HousingRequirements, NeighborhoodRecommendation, Message


def research_neighborhoods(
    requirements: HousingRequirements,
    conversation_history: List[Message]
) -> NeighborhoodRecommendation:
    """
    Researches and recommends neighborhoods based on user requirements.
    """
    from src.core.config import client  # Import here to avoid circular dependencies

    prompt = f"""You are a housing expert specializing in Kenyan cities, particularly {requirements.target_location}.

Research and recommend neighborhoods that:
1. Fit within budget of KES {requirements.monthly_budget}/month
2. Are near {requirements.workplace_location}
3. Have good security features

For EACH neighborhood include:
- Security rating (1-5 stars)
- Detailed security information (neighborhood watch, lighting, police proximity, crime stats, gated communities, guards)
- Distance to workplace
- Transportation options (matatus, boda bodas, accessibility)
- Amenities (markets, hospitals, schools, shopping centers)
- Pros and cons

Provide 3-5 neighborhoods. Be realistic about the budget constraints in Kenya.

Target city: {requirements.target_location}
Workplace: {requirements.workplace_location}
Budget: KES {requirements.monthly_budget}
Preferences: {requirements.preferences or "None"}

Return your response in JSON format matching this structure:
{{
  "neighborhoods": [
    {{
      "name": "string",
      "distance_to_cbd": "string",
      "average_rent_1br": "string (in KES)",
      "average_rent_2br": "string (in KES)",
      "security_rating": "string (e.g., '4/5 stars')",
      "security_details": "string (detailed paragraph about security features)",
      "amenities": ["string"],
      "transportation": "string",
      "description": "string",
      "pros": ["string"],
      "cons": ["string"]
    }}
  ]
}}

Return ONLY valid JSON, no markdown formatting."""

    response = client.models.generate_content(
        model="models/gemini-flash-latest",  # Updated model name
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.5,
            response_mime_type="application/json"
        ),
    )

    parsed = json.loads(response.text)
    return NeighborhoodRecommendation(**parsed)