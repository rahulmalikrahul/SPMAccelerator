import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="SPM AI Accelerator", layout="wide")

# --- SIDEBAR: FREE API SETUP ---
st.sidebar.title("Settings")
# User can get a free key at https://aistudio.google.com/app/apikey
api_key = st.sidebar.text_input("Enter Google Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.sidebar.warning("Please enter your free Google Gemini API key to use AI features.")

# --- NAVIGATION ---
menu = ["Home & ROI Dashboard", "AI Consultant Bot", "Consultant Onboarding", "Sample Data Viewer"]
choice = st.sidebar.selectbox("Navigate to", menu)

# --- MODULE 1: ROI DASHBOARD ---
if choice == "Home & ROI Dashboard":
    st.title("🚀 ServiceNow SPM AI Accelerator")
    st.markdown("### Strategic Implementation & Value Realization")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Manual Setup Time", "120 Hours", "-80%")
    with col2:
        st.metric("AI-Assisted Setup", "24 Hours", "Success")
    with col3:
        st.metric("Estimated Cost Savings", "$15,000", "Per Project")

    st.divider()
    st.subheader("Quantitative Benefits (ROI)")
    roi_data = {
        "Phase": ["Requirements Gathering", "User Stories", "UAT Testing", "Data Migration"],
        "Manual (Days)": [10, 5, 8, 12],
        "AI-Accelerated (Days)": [2, 0.5, 2, 3],
        "Efficiency Gain": ["80%", "90%", "75%", "75%"]
    }
    st.table(pd.DataFrame(roi_data))

# --- MODULE 2: AI CONSULTANT BOT ---
elif choice == "AI Consultant Bot":
    st.title("🤖 SPM Expert Consultant")
    st.info("Ask me about SPM Best Practices, CSDM alignment, or Demand Management.")
    
    user_input = st.text_input("Your Question:")
    if user_input and api_key:
        with st.spinner("Analyzing ServiceNow Best Practices..."):
            response = model.generate_content(f"Act as a ServiceNow SPM expert consultant. Answer this: {user_input}")
            st.markdown(response.text)
    elif not api_key:
        st.error("Please provide an API key in the sidebar.")

# --- MODULE 3: ONBOARDING ---
elif choice == "Consultant Onboarding":
    st.title("🎓 Consultant Training Hub")
    st.markdown("""
    ### 1. Fundamentals
    * [ ] Understand the difference between Demand and Project.
    * [ ] Learn the CSDM 4.0 lifecycle.
    ### 2. Implementation Quiz
    **Scenario:** A client wants to use Projects without Demands. What do you advise?
    """)
    if st.button("Get AI Recommendation"):
        if api_key:
            res = model.generate_content("Provide a professional recommendation for a ServiceNow consultant when a client wants to skip Demand management.")
            st.write(res.text)

# --- MODULE 4: DATA VIEWER ---
elif choice == "Sample Data Viewer":
    st.title("📊 SPM Sample Data Analysis")
    try:
        df = pd.read_csv("spm_sample_data.csv")
        st.dataframe(df)
        st.bar_chart(df['Portfolio'].value_counts())
    except FileNotFoundError:
        st.error("No sample data found. Run 'data_generator.py' first!")