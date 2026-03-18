# main.py

# 1. MOCK DATABASE (Wait for Step 5 to add real data)
users = [] 

# 2. GUARDRAIL LAYER
def validate_safety(user_input):
    forbidden = ["dangerous", "ghetto", "crime", "sketchy"]
    if any(word in user_input.lower() for word in forbidden):
        return False, "REFRAME: I can help you compare areas based on lighting and transit instead of subjective labels."
    return True, "Safe"

# 3. UI/AUTH FLOW
def start_app():
    print("--- HOUSING RECOMMENDATION SYSTEM ---")
    name = input("Enter Full Name: ")
    email = input("Enter Email: ")
    emergency = input("Emergency Contact: ")
    
    # Save user to 'database'
    users.append({"name": name, "email": email, "emergency": emergency})
    print(f"\nWelcome {name}! Your profile is set up.")

    # Input Layer
    location = input("\nEnter Target City: ")
    budget = input("Enter Budget: ")
    query = input("Any specific safety concerns? ")

    # Run through Guardrails
    is_valid, message = validate_safety(query)
    if not is_valid:
        print(f"\n[ALERT] {message}")
    else:
        print("\nSearching for houses in", location, "with budget", budget, "...")

if __name__ == "__main__":
    start_app()