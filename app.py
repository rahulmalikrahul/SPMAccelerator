import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="SPM AI Accelerator", page_icon="🚀", layout="wide")

# --- API KEY & MODEL SETUP ---
secret_key = st.secrets.get("GEMINI_API_KEY")
st.sidebar.title("🔐 API Configuration")

if secret_key:
    api_key = secret_key
    st.sidebar.success("✅ API Key loaded from Secrets")
else:
    # Manual input if secrets fail
    api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")
    if not api_key:
        st.sidebar.warning("⚠️ Key required to enable AI")

ai_ready = False
if api_key:
    try:
        genai.configure(api_key=api_key)
        # Using Gemini 3 Flash (Standard as of March 2026)
        model = genai.GenerativeModel('gemini-3-flash')
        ai_ready = True
    except Exception as e:
        st.sidebar.error(f"Connection Error: {e}")

# --- NAVIGATION ---
menu = ["Value Dashboard", "🤖 AI Consultant", "📋 CSDM 4.0 Auditor", "🎓 Onboarding Hub", "📂 Data Explorer"]
choice = st.sidebar.radio("Navigate Modules", menu)

# --- MODULE 1: VALUE DASHBOARD ---
if choice == "Value Dashboard":
    st.title("📈 Implementation Value Realization")
    m1, m2, m3 = st.columns(3)
    m1.metric("Delivery Speed", "4.5x Faster", "82% Improvement")
    m2.metric("OOTB Alignment", "95%", "High Quality")
    m3.metric("Projected Savings", "$22,500", "Per Lifecycle")
    st.divider()
    st.subheader("Quantitative Benefits Table")
    roi_data = {
        "Task": ["Process Design", "User Story Writing", "Data Migration"],
        "Manual (Days)": [15, 7, 5],
        "AI-Assisted (Days)": [3, 0.5, 1]
    }
    st.table(pd.DataFrame(roi_data))

# --- MODULE 2: CSDM 4.0 AUDITOR ---
elif choice == "📋 CSDM 4.0 Auditor":
    st.title("📋 CSDM 4.0 Best Practice Auditor")
    st.write("Check your architecture against ServiceNow's latest CSDM domains.")
    
    mapping_input = st.text_area("Describe your table mapping (e.g., 'Mapping legacy apps to Business Services'):")
    
    if st.button("Run Audit"):
        if ai_ready:
            with st.spinner("Auditing against CSDM 4.0..."):
                # Fixed triple-quote structure
                prompt = f"""
                Act as a ServiceNow Master Architect. 
                Audit this implementation plan: {mapping_input}.
                Verify alignment with CSDM 4.0 domains.
                Provide a score (1-10) and specific Red Flags for the build phase.
                """
                response = model.generate_content(prompt)
                st.info("### Audit Results")
                st.markdown(response.text)
        else:
            st.error("AI Key Required for Audit.")

# --- MODULE 3: AI CONSULTANT ---
elif choice == "🤖 AI Consultant":
    st.title("🤖 Virtual SPM Lead")
    if ai_ready:
        query = st.text_input("Ask a question about SPM Best Practices:")
        if st.button("Generate Solution"):
            with st.spinner("Analyzing..."):
                res = model.generate_content(f"Act as a ServiceNow SPM expert. Use CSDM 4.0 standards. Query: {query}")
                st.markdown("---")
                st.markdown(res.text)
    else:
        st.error("API Key Required.")

# --- MODULE 4: ONBOARDING ---
elif choice == "Onboarding Hub":
    st.title("🎓 Training Hub")
    st.info("**Scenario:** A client wants to track costs in Excel instead of ServiceNow SPM.")
    ans = st.text_area("Your advice as a consultant:")
    if st.button("Grade Me"):
        if ai_ready:
            with st.spinner("Grading..."):
                res = model.generate_content(f"Grade this consultant's answer based on ServiceNow SPM best practices: {ans}")
                st.success("Expert Feedback:")
                st.write(res.text)

# --- MODULE 5: DATA EXPLORER ---
elif choice == "Data Explorer":
    st.title("📂 Sample Portfolio Data")
    if os.path.exists("spm_sample_data.csv"):
        df = pd.read_csv("spm_sample_data.csv")
        st.dataframe(df, use_container_width=True)
        st.bar_chart(df["Portfolio"].value_counts())
    else:
        st.warning("⚠️ Data file not found. Ensure 'spm_sample_data.csv' is in the root directory.")