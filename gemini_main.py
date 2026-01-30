import os
import json
from typing import List, Dict, Optional, TypedDict
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize Gemini client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

#  DO NOT TOUCH
#  IMPORTANT FOR DEBUGGING PURPOSES
# 
# def list_available_models():
#     """List all available models for debugging."""
#     try:
#         models = client.models.list()
#         print("Available models:")
#         for model in models:
#             print(f"  - {model.name}")
#     except Exception as e:
#         print(f"Error listing models: {e}")


# # List available models for reference
# print("=" * 80)
# list_available_models()
# print("=" * 80)


# Define Pydantic models for structured outputs
class HousingRequirements(BaseModel):
    has_all_details: bool
    current_location: Optional[str] = ""
    target_location: Optional[str] = ""
    workplace_location: Optional[str] = ""
    monthly_budget: Optional[float] = 0
    preferences: Optional[str] = ""


class Neighborhood(BaseModel):
    name: str
    distance_to_cbd: str
    average_rent_1br: str
    average_rent_2br: str
    security_rating: str
    security_details: str
    amenities: List[str]
    transportation: str
    description: str
    pros: List[str]
    cons: List[str]


class NeighborhoodRecommendation(BaseModel):
    neighborhoods: List[Neighborhood]


class Message(TypedDict):
    role: str
    content: str


# Agent 1: Triage - Check if we have all information
def triage_user_input(
    user_input: str, 
    conversation_history: List[Message]
) -> HousingRequirements:
    """
    Analyzes user input to determine if we have all required information
    for housing recommendations.
    """
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

    # Add current user input
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part(text=user_input)]
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
    return HousingRequirements(**parsed)


# Agent 2: Gather missing details
def gather_missing_details(
    requirements: HousingRequirements,
    conversation_history: List[Message]
) -> str:
    """
    Asks user for missing information in a friendly way.
    """
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

    response = client.models.generate_content(
        model="models/gemini-flash-latest",  # Updated model name
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.7),
    )

    return response.text or "Could you provide more details about your relocation?"


# Agent 3: Research neighborhoods
def research_neighborhoods(
    requirements: HousingRequirements,
    conversation_history: List[Message]
) -> NeighborhoodRecommendation:
    """
    Researches and recommends neighborhoods based on user requirements.
    """
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


# Agent 4: Present recommendations
def present_recommendations(
    recommendations: NeighborhoodRecommendation,
    requirements: HousingRequirements,
    conversation_history: List[Message]
) -> str:
    """
    Formats and presents recommendations in a user-friendly way.
    """
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

    response = client.models.generate_content(
        model="models/gemini-flash-latest",  # Updated model name
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.7),
    )

    return response.text or "Here are your recommendations."


# Main workflow function
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

        # Step 1: Triage - check if we have all needed information
        print("📋 Step 1: Analyzing your requirements...")
        requirements = triage_user_input(user_input, conversation_history)
        
        print(f"Requirements: {requirements.model_dump_json(indent=2)}\n")

        # Step 2: Branch based on whether we have complete information
        if requirements.has_all_details:
            print("✅ All details collected. Researching neighborhoods...\n")

            # Step 3: Research neighborhoods
            print("🔍 Step 2: Searching for suitable neighborhoods...")
            recommendations = research_neighborhoods(requirements, conversation_history)

            print(f"Found {len(recommendations.neighborhoods)} neighborhoods\n")

            # Step 4: Present recommendations
            print("📝 Step 3: Preparing your personalized recommendations...\n")
            presentation = present_recommendations(recommendations, requirements, conversation_history)

            return {
                "status": "success",
                "requirements": requirements.model_dump(),
                "recommendations": recommendations.model_dump(),
                "message": presentation
            }
        else:
            print("❓ Missing some information...\n")

            # Ask for missing details
            follow_up_question = gather_missing_details(requirements, conversation_history)

            return {
                "status": "needs_more_info",
                "requirements": requirements.model_dump(),
                "message": follow_up_question
            }

    except Exception as error:
        print(f"Error running housing agent: {error}")
        import traceback
        traceback.print_exc()
        raise


# Interactive chat function
def interactive_chat():
    """
    Run an interactive chat session with the housing agent.
    """
    print("\n" + "=" * 80)
    print("🏠 WELCOME TO KENYA HOUSING RELOCATION ASSISTANT")
    print("=" * 80)
    print("\nI'll help you find safe and affordable housing in Kenya.")
    print("Just tell me about your relocation plans!\n")
    
    conversation_history = []
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                print("\n👋 Thank you for using the housing assistant. Goodbye!")
                break
            
            result = run_housing_agent(user_input, conversation_history)
            
            # Add user input to history
            conversation_history.append({"role": "user", "content": user_input})
            
            # Print assistant's response
            print(f"\n🤖 Assistant: {result['message']}")
            
            # Add assistant response to history
            conversation_history.append({"role": "assistant", "content": result['message']})
            
            # If we have recommendations, offer to save them
            if result['status'] == 'success':
                save_choice = input("\n📁 Would you like to save these recommendations to a file? (yes/no): ").strip().lower()
                if save_choice in ['yes', 'y']:
                    filename = f"housing_recommendations_{result['requirements']['target_location'].replace(' ', '_')}.json"
                    with open(filename, "w") as f:
                        json.dump(result, f, indent=2)
                    print(f"💾 Recommendations saved to {filename}")
                    
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("Please try again or type 'quit' to exit.")


# Example usage
def main():
    """
    Example of how to use the housing agent.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE USAGE")
    print("=" * 80)
    
    # Option 1: Run interactive chat
    interactive_chat()
    
    # Option 2: Run a single example (uncomment to use)
    """
    # Example 1: Complete information
    user_input = (
        "I'm relocating from Nairobi to Kisumu for a new accounting job in Kisumu CBD. "
        "My budget is 25,000 shillings per month. I need a secure neighborhood with good "
        "lighting and preferably near police stations."
    )
    
    result = run_housing_agent(user_input)
    
    print("\n" + "=" * 80)
    print("RESULT")
    print("=" * 80 + "\n")
    print(result["message"])
    print("\n" + "=" * 80)
    
    # Save to file
    with open("housing_recommendations.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\n💾 Full results saved to housing_recommendations.json")
    """


if __name__ == "__main__":
    main()