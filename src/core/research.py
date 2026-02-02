import json
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from src.models.housing_models import HousingRequirements, NeighborhoodRecommendation, Message
from src.core.safety_guardrails import inject_safety_context, postprocess_response


def extract_json_from_response(response_text: str) -> str:
    """
    Extracts a valid JSON object from an AI response that may contain
    additional text, markdown formatting, or multiple JSON objects.
    
    Args:
        response_text: The raw AI response text
        
    Returns:
        Extracted JSON string suitable for parsing
    """
    # Find the first occurrence of '{' and the last occurrence of '}'
    start_index = response_text.find('{')
    end_index = response_text.rfind('}')
    
    if start_index == -1 or end_index == -1:
        # No JSON found, try to clean and return the original
        return response_text
    
    # Extract the JSON portion
    json_str = response_text[start_index:end_index + 1]
    
    # Attempt to validate it's proper JSON by checking balance
    try:
        # Check if braces are balanced
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')
        
        if open_braces != close_braces:
            # Try to find the correct closing brace
            # This is a fallback for malformed JSON
            depth = 0
            for i, char in enumerate(json_str):
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        json_str = json_str[:i + 1]
                        break
    except Exception:
        pass
    
    return json_str


def research_neighborhoods(
    requirements: HousingRequirements,
    conversation_history: List[Message],
    user_context: Optional[Dict[str, Any]] = None
) -> NeighborhoodRecommendation:
    """
    Researches and recommends neighborhoods based on user requirements.
    
    IMPORTANT: This function follows Documentation-guide principles:
    - Advisory, not authoritative
    - Focus on trade-offs, not predictions
    - No stereotyping or labeling areas
    """
    from src.core.config import client  # Import here to avoid circular dependencies

    # Build the base prompt with safety-aware instructions
    prompt = f"""You are an ADVISORY housing expert. Your role is to help users understand
trade-offs between different housing options, NOT to label areas as safe or dangerous.

IMPORTANT GUIDELINES:
1. Do NOT give security ratings (1-5 stars) - this labels neighborhoods
2. Focus on FACTORS TO CONSIDER: commute, budget, amenities, transport
3. Present BALANCED perspectives - every area has diverse communities
4. Use neutral language: "factors to consider" not "dangerous areas"
5. Acknowledge uncertainty: "considerations include" not "this is safe"

Research neighborhoods that fit the user's criteria:
1. Within budget of KES {requirements.monthly_budget}/month
2. Near {requirements.workplace_location} or with reasonable commute
3. With various amenity and transportation options

For EACH neighborhood, include:
- Location and distance to key landmarks
- Rent ranges for different unit types
- Transportation options (matatus, bodaboda, accessibility)
- Amenities (markets, hospitals, schools, shopping)
- Key trade-offs to consider (cost vs commute vs amenities)
- Notable characteristics that might matter to the user

Provide 3-5 neighborhoods that fit the budget constraints. Be realistic about
what's available at {requirements.monthly_budget} KES/month in {requirements.target_location}.

Target city: {requirements.target_location}
Workplace area: {requirements.workplace_location}
Budget: KES {requirements.monthly_budget}/month
Preferences: {requirements.preferences or "Not specified - focus on budget and commute"}

Return your response in JSON format:
{{
  "neighborhoods": [
    {{
      "name": "string",
      "distance_to_cbd": "string",
      "distance_to_workplace": "string",
      "average_rent_1br": "string (in KES)",
      "average_rent_2br": "string (in KES)",
      "transportation": "string (matatu routes, accessibility)",
      "amenities": ["array of nearby amenities"],
      "key_tradeoffs": "string describing main considerations",
      "description": "string with balanced overview",
      "factors_to_consider": ["array of specific points"],
      "general_notes": "string with any caveats"
    }}
  ]
}}

Return ONLY valid JSON, no markdown formatting."""

    # Inject safety context
    safe_prompt = inject_safety_context(prompt, user_context)

    response = client.models.generate_content(
        model="models/gemini-flash-latest",
        contents=safe_prompt,
        config=types.GenerateContentConfig(
            temperature=0.5,
            response_mime_type="application/json"
        ),
    )

    # Post-process to ensure no authoritative claims slipped through
    cleaned_response = postprocess_response(response.text)
    
    # Extract JSON portion from response (handles markdown, extra text, etc.)
    json_response = extract_json_from_response(cleaned_response)
    
    parsed = json.loads(json_response)
    return NeighborhoodRecommendation(**parsed)

