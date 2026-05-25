from typing import Dict, List, Optional
from app.schemas.housing_models import HousingRequirements, NeighborhoodRecommendation, Message
from app.ai import get_ai_provider
from app.services.guardrails import check_input
from app.services.risk_engine import evaluate_risk, RiskProfile
import json
import logging

logger = logging.getLogger(__name__)

# Token limits per AI call — keeps costs bounded and responses focused
_TOKENS_TRIAGE = 300
_TOKENS_MISSING = 150
_TOKENS_RESEARCH = 2000
_TOKENS_PRESENT = 1500


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
            response_format="json",
            max_tokens=_TOKENS_TRIAGE,
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
            response_format="text",
            max_tokens=_TOKENS_MISSING,
        )

        return response_text or "Could you provide more details about your relocation?"

    def research_neighborhoods(
        self,
        requirements: HousingRequirements,
        risk_profile: RiskProfile,
    ) -> NeighborhoodRecommendation:
        """Research and recommend neighborhoods based on requirements and risk profile."""
        logger.info("🔍 Step 2: Researching neighborhoods...")

        risk_context = (
            f"Situational risk level: {risk_profile.level} (score: {risk_profile.score}/9)\n"
            f"Risk factors identified:\n" +
            "\n".join(f"  - {f}" for f in risk_profile.factors)
        ) if risk_profile.factors else f"Situational risk level: {risk_profile.level}"

        prompt = f"""You are a housing expert specializing in Kenyan cities, particularly {requirements.target_location}.

The user has been assessed with the following situational risk profile (determined by fixed rules, not your judgment):
{risk_context}

Use this risk profile to filter and prioritize neighborhoods — do NOT re-assess the risk level yourself.
For a Higher risk profile, only recommend neighborhoods with security rating 4/5 or above.
For a Medium risk profile, recommend neighborhoods with security rating 3/5 or above.
For a Low risk profile, include all neighborhoods within budget.

Research and recommend neighborhoods that:
1. Fit within budget of KES {requirements.monthly_budget}/month
2. Are near {requirements.workplace_location}
3. Match the security threshold for the risk level above

For EACH neighborhood include:
- Approximate latitude and longitude coordinates for map visualization
- Security rating (1-5 stars)
- Detailed security information (neighborhood watch, lighting, police proximity, gated communities, guards)
- Distance to workplace
- Transportation options (matatus, boda bodas, accessibility)
- Amenities (markets, hospitals, schools, shopping centers)
- Pros and cons

Provide 3-5 neighborhoods. Be realistic about budget constraints in Kenya.

Target city: {requirements.target_location}
Workplace: {requirements.workplace_location}
Budget: KES {requirements.monthly_budget}
Preferences: {requirements.preferences or "None"}

Return your response in JSON format matching this structure:
{{
  "neighborhoods": [
    {{
      "name": "string",
      "latitude": number,
      "longitude": number,
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
            response_format="json",
            max_tokens=_TOKENS_RESEARCH,
        )

        parsed = json.loads(response_text)
        recommendations = NeighborhoodRecommendation(**parsed)

        logger.info(f"Found {len(recommendations.neighborhoods)} neighborhoods")
        return recommendations

    def present_recommendations(
        self,
        recommendations: NeighborhoodRecommendation,
        requirements: HousingRequirements,
        risk_profile: RiskProfile,
    ) -> str:
        """Format and present recommendations in a user-friendly way."""
        logger.info("📝 Step 3: Preparing recommendations...")

        risk_explanation = (
            f"Risk level: {risk_profile.level}. "
            f"Reasons: {'; '.join(risk_profile.factors)}."
            if risk_profile.factors
            else f"Risk level: {risk_profile.level}."
        )

        prompt = f"""You are a helpful housing assistant presenting neighborhood recommendations.

The user's situational risk was assessed as: {risk_explanation}
Explain this risk assessment briefly at the start so the user understands why certain neighborhoods were prioritised.

Create a clear, friendly summary that includes:
1. Brief introduction acknowledging their move to {requirements.target_location} and their risk level
2. Each neighborhood recommendation with:
   - Name and location
   - Rent range
   - Security highlights (emphasize this!)
   - Distance/commute to {requirements.workplace_location}
   - Key amenities
   - Notable pros and cons
3. Practical next steps (viewing properties, contacting agents, verification tips)
4. A short disclaimer that this is advisory information only

Use clear formatting with headers and bullet points. Be encouraging and helpful.

Target city: {requirements.target_location}
Workplace: {requirements.workplace_location}

Recommendations JSON:
{recommendations.model_dump_json()}"""

        response_text = self.ai_provider.generate_content(
            contents=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format="text",
            max_tokens=_TOKENS_PRESENT,
        )

        return response_text or "Here are your recommendations."

    def process_housing_request(
        self,
        user_input: str,
        conversation_history: Optional[List[Message]] = None,
        time_of_day: str = "Day",
        commute_distance_km: float = 1.0,
        living_arrangement: str = "Alone",
        safety_tolerance: str = "Medium",
        budget_kes: float = 20000,
    ) -> Dict:
        """Main orchestration method for housing recommendations."""
        logger.info("🏠 Starting housing recommendation agent...")

        if conversation_history is None:
            conversation_history = []

        # Issue 1 — Guardrails: check input before anything else
        guard = check_input(user_input)
        if not guard["allowed"]:
            logger.info("🚫 Guardrail triggered — returning reframe message")
            return {"status": "blocked", "message": guard["message"]}

        # Issue 4 — Risk Engine: deterministic scoring before any AI call
        risk_profile = evaluate_risk(
            time_of_day=time_of_day,
            commute_distance_km=commute_distance_km,
            living_arrangement=living_arrangement,
            safety_tolerance=safety_tolerance,
            budget_kes=budget_kes,
        )
        logger.info(f"⚠️ Risk profile: {risk_profile.level} (score {risk_profile.score})")

        # Step 1: Triage — extract requirements from user input
        requirements = self.triage_requirements(user_input, conversation_history)

        # Step 2: Branch based on completeness
        if requirements.has_all_details:
            logger.info("✅ All details collected. Researching neighborhoods...")

            recommendations = self.research_neighborhoods(requirements, risk_profile)
            presentation = self.present_recommendations(recommendations, requirements, risk_profile)

            return {
                "status": "success",
                "risk_profile": {
                    "level": risk_profile.level,
                    "score": risk_profile.score,
                    "factors": risk_profile.factors,
                },
                "requirements": requirements.model_dump(),
                "recommendations": recommendations.model_dump(),
                "message": presentation,
            }
        else:
            follow_up_question = self.gather_missing_details(requirements)
            return {
                "status": "needs_more_info",
                "requirements": requirements.model_dump(),
                "message": follow_up_question,
            }
