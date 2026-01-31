from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from src.models.housing_models import NeighborhoodRecommendation, HousingRequirements, Message
from src.core.safety_guardrails import inject_safety_context, postprocess_response


def present_recommendations(
    recommendations: NeighborhoodRecommendation,
    requirements: HousingRequirements,
    conversation_history: List[Message],
    user_context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Formats and presents recommendations in a user-friendly, advisory way.
    
    IMPORTANT: Follow Documentation-guide principles:
    - Advisory, not authoritative
    - Focus on trade-offs, not labels
    - Include advisory disclaimers
    - Use positive framing (strategies residents use, not dangers to avoid)
    - Respect user's personal risk tolerance
    """
    from src.core.config import client  # Import here to avoid circular dependencies

    prompt = f"""You are a helpful, ADVISORY housing assistant helping someone relocate to {requirements.target_location}.

Create a clear, balanced summary following these ethical guidelines:

1. ADVISORY TONE: Use "Based on your criteria..." or "Strategies residents use..." not "You should..."
2. NO AUTHORITATIVE CLAIMS: Avoid "This area is safe" or similar definitive statements
3. POSITIVE FRAMING: Focus on what residents DO to navigate areas safely, not what to avoid
4. USER-CENTERED: Reference the user's risk tolerance ({requirements.risk_tolerance.value if requirements.risk_tolerance else 'medium'}) and return time preferences
5. EMPOWERMENT-FOCUSED: Share community strategies, tech solutions, and practical tips
6. CONTEXTUAL FACTORS: Include info about lighting, transport hours, community initiatives

Structure your response:
1. Brief, welcoming intro acknowledging their move and risk preferences
2. Each neighborhood with:
   - Name and general location
   - Rent range
   - Key trade-offs (cost vs commute vs amenities)
   - Strategies residents use in this area (community resources, transport tips)
   - Factors to consider based on their return time and transport mode
3. Personalized safety considerations for their profile
4. Practical next steps (viewing properties, what to ask agents, community groups to join)
5. Advisory disclaimer at the end

NEVER SAY:
- "This area is dangerous/safe"
- "Avoid this area"
- "High crime area"

INSTEAD SAY:
- "For your evening return time, consider these strategies residents use..."
- "This area has limited street lighting - many residents use ride-hailing after dark"
- "Community WhatsApp groups help residents share real-time transport info"
- "Compared to other options, this area has better/worse transport availability at night"

Target city: {requirements.target_location}
Workplace area: {requirements.workplace_location}
Budget: KES {requirements.monthly_budget}/month
Risk tolerance: {requirements.risk_tolerance.value if requirements.risk_tolerance else 'medium'}
Typical return time: {requirements.typical_return_time.value if requirements.typical_return_time else 'evening'}
Transport mode: {requirements.transport_mode.value if requirements.transport_mode else 'matatu'}

Recommendations to present:
{recommendations.model_dump_json()}"""

    # Inject safety context
    safe_prompt = inject_safety_context(prompt, user_context)

    response = client.models.generate_content(
        model="models/gemini-flash-latest",
        contents=safe_prompt,
        config=types.GenerateContentConfig(temperature=0.7),
    )

    raw_text = response.text or "Here are your recommendations."
    
    # Post-process to ensure no authoritative claims
    cleaned_text = postprocess_response(raw_text)
    
    # Ensure advisory disclaimer is present with empowerment focus
    if "advisory" not in cleaned_text.lower() or "visit" not in cleaned_text.lower():
        cleaned_text += "\n\n*This is advisory information to help you start your search. Always visit areas personally, talk to locals about their experiences, and consider joining community groups for current insights. Your personal risk tolerance is unique - what works for others may not work for you.*"
    
    return cleaned_text

