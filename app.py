import streamlit as st
import google.generativeai as genai

# 1. SETUP GEMINI
genai.configure(api_key="PASTE_YOUR_KEY_HERE")
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. UI HEADER
st.set_page_config(page_title="Nyali Housing Advisor", page_icon="🏠")
st.title("🏠 Housing & Safety Advisory Agent")
st.markdown("Find the best neighborhoods based on your budget and safety needs.")

# 3. SIDEBAR (User Profile)
with st.sidebar:
    st.header("User Profile")
    name = st.text_input("Full Name")
    emergency = st.text_input("Emergency Contact")
    st.info("Profile data is stored for your session.")

# 4. INPUT LAYER (Main Page)
col1, col2 = st.columns(2)
with col1:
    location = st.text_input("Target City/Town", value="Kisumu")
    budget = st.number_input("Monthly Budget (KES)", min_value=5000, step=1000)
with col2:
    arrangement = st.selectbox("Living Arrangement", ["Alone", "Shared"])
    safety_pref = st.select_slider("Safety Tolerance", options=["Low", "Medium", "High"])

query = st.text_area("Specific safety concerns or preferences?")

# 5. PROCESSOR
if st.button("Get Recommendations"):
    # Guardrail Check
    forbidden = ["dangerous", "ghetto", "crime", "sketchy"]
    if any(word in query.lower() for word in forbidden):
        st.warning("⚠️ REFRAME: I can help you compare areas based on lighting and transit instead of subjective labels.")
    else:
        with st.spinner("AI is analyzing neighborhoods..."):
            prompt = f"Give 3 neighborhood recommendations in {location} for {budget} KES budget. Focus on {arrangement} living and {safety_pref} safety tolerance. Focus on situational safety like lighting and transport."
            response = model.generate_content(prompt)
            st.success("Analysis Complete!")
            st.markdown(response.text)