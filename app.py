import streamlit as st
import google.generativeai as genai

# Configuration
genai.configure(api_key="PASTE_YOUR_KEY_HERE")
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "users_db" not in st.session_state:
    st.session_state.users_db = {}
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# --- AUTH FLOW ---
def auth_flow():
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.title("🔐 Login")
        with st.form("login"):
            email = st.text_input("Email/Username")
            st.text_input("Password", type="password")
            if st.form_submit_button("Sign In"):
                st.session_state.logged_in = True
                st.session_state.last_email_entered = email
                # Fetch user from 'DB' or create guest profile
                st.session_state.current_user = st.session_state.users_db.get(
                    email, {"name": email if email else "Guest", "emergency": "N/A"}
                )
                st.rerun()

    with tab2:
        st.title("📝 Sign Up")
        with st.form("signup"):
            name = st.text_input("Full Name")
            reg_email = st.text_input("Email")
            emergency = st.text_input("Emergency Contact")
            st.text_input("Password", type="password")
            if st.form_submit_button("Create Account"):
                st.session_state.users_db[reg_email] = {"name": name, "emergency": emergency}
                st.success("Account created! Now go to the Login tab.")

# --- MAIN APP ---
def main_app():
    user = st.session_state.current_user
    
    # 1. SIDEBAR (Component 5.3: User Profile & Session State)
    with st.sidebar:
        st.header("👤 Profile")
        st.write(f"**User:** {user.get('name')}")
        st.write(f"**Email:** {st.session_state.get('last_email_entered')}")
        st.write(f"**Emergency:** {user.get('emergency')}")
        st.divider()
        if st.button("Log Out", type="primary", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # 2. MAIN INPUTS (Component 5.1: Input Layer)
    st.title("🏠 Smart Housing Advisor")
    
    with st.expander("📍 Location & Commute", expanded=True):
        col1, col2 = st.columns(2)
        location = col1.text_input("City/Town", placeholder="e.g. Kisumu")
        destination = col2.text_input("Commute Destination", placeholder="e.g. Town Center")
        
        col3, col4 = st.columns(2)
        dist = col3.number_input("Distance (KM)", min_value=0.1)
        time = col4.selectbox("Return Time", ["Day", "Night"])

    with st.expander("💰 Preferences"):
        budget = st.select_slider("Budget (KES)", options=[10000, 20000, 35000, 50000, 75000, 100000])
        col5, col6 = st.columns(2)
        safety = col5.select_slider("Safety Tolerance", ["Low", "Medium", "High"])
        arrangement = col6.selectbox("Living Arrangement", ["Alone", "Shared"])

    query = st.text_area("Specific safety concerns?")

    # 3. LOGIC (Component 5.2: Guardrails)
    if st.button("Generate My Advisor Report"):
        forbidden = ["dangerous", "ghetto", "crime", "sketchy"]
        if not location:
            st.error("Please enter a location.")
        elif any(word in query.lower() for word in forbidden):
            st.warning("🛡️ REFRAME: I can help you compare housing options based on situational factors like lighting and transit proximity.")
        else:
            with st.spinner("Consulting AI..."):
                prompt = f"Housing Advisor: Recommend 3 areas in {location} for {budget} KES. Commute: {dist}km to {destination} at {time}. Arrangement: {arrangement}. Safety: {safety}. Specifics: {query}."
                response = model.generate_content(prompt)
                st.success("Analysis Complete")
                st.markdown(response.text)

# Execution
if st.session_state.logged_in:
    main_app()
else:
    auth_flow()