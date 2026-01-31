from typing import List, Dict, Optional
from src.models.housing_models import Message, HousingRequirements, NeighborhoodRecommendation
from src.core.triage import triage_user_input
from src.core.gather_details import gather_missing_details
from src.core.research import research_neighborhoods
from src.core.presentation import present_recommendations
from src.core.safety_guardrails import inject_safety_context


def run_housing_agent(user_input: str, conversation_history: Optional[List[Message]] = None) -> Dict:
    """
    Main function that orchestrates the housing recommendation workflow.

    Args:
        user_input: User's query about housing
        conversation_history: Optional history of previous messages

    Returns:
        Dictionary with status and either recommendations or follow-up questions
    """
    if conversation_history is None:
        conversation_history = []

    try:
        print("🏠 Starting housing recommendation agent...\n")

        # Step 0: Safety check on user input (handled in triage)
        warning_message = None
        advisory_disclaimer = None

        # Step 1: Triage - check if we have all needed information
        print("📋 Step 1: Analyzing your requirements...")
        triage_result = triage_user_input(user_input, conversation_history)
        
        # Handle both old and new return types for backwards compatibility
        if isinstance(triage_result, tuple) and len(triage_result) == 3:
            requirements, warning_message, advisory_disclaimer = triage_result
        else:
            requirements = triage_result

        print(f"Requirements: {requirements.model_dump_json(indent=2)}\n")

        # Step 2: Branch based on whether we have complete information
        if requirements.has_all_details:
            print("✅ All details collected. Researching neighborhoods...\n")

            # Step 3: Research neighborhoods (with safety context)
            print("🔍 Step 2: Searching for suitable neighborhoods...")
            
            # Build user context for safety injection
            user_context = {
                'budget': requirements.monthly_budget,
                'location': requirements.target_location,
                'workplace': requirements.workplace_location
            }
            
            recommendations = research_neighborhoods(requirements, conversation_history, user_context)

            print(f"Found {len(recommendations.neighborhoods)} neighborhoods\n")

            # Step 4: Present recommendations
            print("📝 Step 3: Preparing your personalized recommendations...\n")
            presentation = present_recommendations(recommendations, requirements, conversation_history, user_context)

            # Build response with any safety warnings
            response_data = {
                "status": "success",
                "requirements": requirements.model_dump(),
                "recommendations": recommendations.model_dump(),
                "message": presentation
            }
            
            # Include safety warnings if present
            if warning_message:
                response_data["warning_message"] = warning_message
            if advisory_disclaimer:
                response_data["advisory_disclaimer"] = advisory_disclaimer

            return response_data
        else:
            print("❓ Missing some information...\n")

            # Ask for missing details
            follow_up_question = gather_missing_details(requirements, conversation_history)

            response_data = {
                "status": "needs_more_info",
                "requirements": requirements.model_dump(),
                "message": follow_up_question
            }
            
            # Include safety warnings if present
            if warning_message:
                response_data["warning_message"] = warning_message
            if advisory_disclaimer:
                response_data["advisory_disclaimer"] = advisory_disclaimer

            return response_data

    except Exception as error:
        print(f"Error running housing agent: {error}")
        import traceback
        traceback.print_exc()
        raise

