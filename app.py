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
    api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")
    if not api_key:
        st.sidebar.warning("⚠️ Key required to enable AI")

ai_ready = False
if api_key:
    try:
        genai.configure(api_key=api_key)
        # 2026 Standard Model
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
    roi_data = {"Task": ["Process Design", "User Story Writing", "Data Migration"], "Manual (Days)": [15, 7, 5], "AI-Assisted (Days)": [3, 0.5, 1]}
    st.table(pd.DataFrame(roi_data))

# --- NEW MODULE 2: CSDM 4.0 AUDITOR ---
elif choice == "📋 CSDM 4.0 Auditor":
    st.title("📋 CSDM 4.0 Best Practice Auditor")
    st.write("Input your proposed architecture or table mapping to check alignment with the **CSDM 4.0 Foundation, Design, and Build** domains.")
    
    mapping_input = st.text_area("Describe your mapping (e.g., 'We are mapping our legacy ERP app directly to the Business Service table'):")
    
    if st.button("Run Audit"):
        if ai_ready:
            with st.spinner("Auditing against ServiceNow CSDM 4.0..."):
                prompt = f"""
                Act as a ServiceNow Certified Master Architect. 
                Audit the following implementation plan against CSDM 4.0 standards: {mapping_input}.
                Identify if it correctly uses the 'Business Application' vs 'Application Service' tables.
                Provide a score (1-10)