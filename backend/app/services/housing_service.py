from typing import Dict, List, Optional
from app.schemas.housing_models import HousingRequirements, NeighborhoodRecommendation, Message
from app.ai import get_ai_provider
import json
import logging

logger = logging.getLogger(__name__)


class HousingAdvisoryService:
    """Service for housing advisory operations."""
    
    def __init__(self):
        self.ai_provider = get_ai_provider()
    
    def triage_requirements(self, user_input: str, conversation_history: List[Message]) -> HousingRequirements:
        """Analyze user input to extract housing requirements."""
        logger.info("📋 Step 1: Analyzing requirements...")
        
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

        contents = [{"role": "user", "content": system_content}]
        for msg in conversation_history:
            contents.append({"role": msg["role"], "content": msg["content"]})
        contents.append({"role": "user", "content": user_input})

        response_text = self.ai_provider.generate_content(
            contents=contents,
            temperature=0.3,
            response_format="json"
        )

        parsed = json.loads(response_text)
        requirements = HousingRequirements(**parsed)
        
        logger.info(f"Requirements: {requirements.model_dump_json(indent=2)}")
        return requirements
    
    def gather_missing_details(self, requirements: HousingRequirements) -> str:
        """Generate follow-up question for missing information."""
        logger.info("❓ Missing some information...")
        
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

        response_text = self.ai_provider.generate_content(
            contents=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format="text"
        )

        return response_text or "Could you provide more details about your relocation?"
    
    def research_neighborhoods(self, requirements: HousingRequirements) -> NeighborhoodRecommendation:
        """Research and recommend neighborhoods based on requirements."""
        logger.info("🔍 Step 2: Researching neighborhoods...")
        
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

        response_text = self.ai_provider.generate_content(
            contents=[{"role": "user", "content": prompt}],
            temperature=0.5,
            response_format="json"
        )

        parsed = json.loads(response_text)
        recommendations = NeighborhoodRecommendation(**parsed)
        
        logger.info(f"Found {len(recommendations.neighborhoods)} neighborhoods")
        return recommendations
    
    def present_recommendations(
        self,
        recommendations: NeighborhoodRecommendation,
        requirements: HousingRequirements
    ) -> str:
        """Format and present recommendations in a user-friendly way."""
        logger.info("📝 Step 3: Preparing recommendations...")
        
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

        response_text = self.ai_provider.generate_content(
            contents=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format="text"
        )

        return response_text or "Here are your recommendations."
    
    def process_housing_request(self, user_input: str, conversation_history: Optional[List[Message]] = None) -> Dict:
        """Main orchestration method for housing recommendations."""
        logger.info("🏠 Starting housing recommendation agent...")
        
        if conversation_history is None:
            conversation_history = []

        # Step 1: Triage
        requirements = self.triage_requirements(user_input, conversation_history)

        # Step 2: Branch based on completeness
        if requirements.has_all_details:
            logger.info("✅ All details collected. Researching neighborhoods...")
            
            # Research neighborhoods
            recommendations = self.research_neighborhoods(requirements)
            
            # Present recommendations
            presentation = self.present_recommendations(recommendations, requirements)

            return {
                "status": "success",
                "requirements": requirements.model_dump(),
                "recommendations": recommendations.model_dump(),
                "message": presentation
            }
        else:
            # Ask for missing details
            follow_up_question = self.gather_missing_details(requirements)

            return {
                "status": "needs_more_info",
                "requirements": requirements.model_dump(),
                "message": follow_up_question
            }
