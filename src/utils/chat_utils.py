import json
from typing import List
from src.models.housing_models import Message
from src.core.agent_orchestrator import run_housing_agent


def interactive_chat():
    """
    Run an interactive chat session with the housing agent.
    """
    print("\n" + "=" * 80)
    print("🏠 WELCOME TO KENYA HOUSING RELOCATION ASSISTANT")
    print("=" * 80)
    print("\nI'll help you find safe and affordable housing in Kenya.")
    print("Just tell me about your relocation plans!\n")

    conversation_history: List[Message] = []

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                print("\n👋 Thank you for using the housing assistant. Goodbye!")
                break

            result = run_housing_agent(user_input, conversation_history)

            # Add user input to history
            conversation_history.append({"role": "user", "content": user_input})

            # Print any safety warnings first
            if result.get('warning_message'):
                print(f"\n⚠️  {result['warning_message']}")
            
            # Print advisory disclaimer if present
            if result.get('advisory_disclaimer'):
                print(f"\n📌 {result['advisory_disclaimer']}")

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

