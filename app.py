import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="SPM AI Accelerator", page_icon="🚀", layout="wide")

# --- 🔐 API & SECRETS MANAGEMENT ---
st.sidebar.title("🔐 API Status Hub")

# 1. Attempt to read from Streamlit Secrets
secret_key = st.secrets.get("GEMINI_API_KEY")

if secret_key:
    api_key = secret_key
    st.sidebar.success("✅ Secret Found: Using Streamlit Cloud Secrets")
else:
    # 2. Fallback to manual input if secret is missing
    st.sidebar.warning("⚠️ No Secret Found")
    api_key = st.sidebar.text_input("Enter API Key Manually:", type="password")

# --- AI INITIALIZATION ---
ai_ready = False
model = None

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # DYNAMIC MODEL DISCOVERY (Fixes the 404 Error)
        # We list models to find the best available Flash/Pro model for your key
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Priority list for 2026 models
        priority_models = [
            'models/gemini-3.1-flash-preview', 
            'models/gemini-3-flash-preview', 
            'models/gemini-2.5-flash'
        ]
        
        # Pick the best match from priority list, or fall back to any 'flash' model
        selected_name = next((p for p in priority_models if p in available_models), None)
        if not selected_name:
            selected_name = next((m for m in available_models if 'flash' in m), available_models[0])
            
        model = genai.GenerativeModel(selected_name)
        st.sidebar.info(f"🤖 Brain: {selected_name.replace('models/', '')}")
        ai_ready = True
        
    except Exception as e:
        st.sidebar.error(f"Setup Error: {e}")

# --- APP NAVIGATION ---
menu = ["Value Dashboard", "🤖 AI Consultant", "📋 CSDM 4.0 Auditor", "📂 Data Explorer"]
choice = st.sidebar.radio("Navigate Modules", menu)

# --- MODULE 1: VALUE DASHBOARD ---
if choice == "Value Dashboard":
    st.title("📈 Implementation Value Realization")
    m1, m2, m3 = st.columns(3)
    m1.metric("Delivery Speed", "4.5x Faster", "82% Improvement")
    m2.metric("OOTB Alignment", "95%", "High Quality")
    m3.metric("Projected Savings", "$22,500", "Per Lifecycle")
    
    st.divider()
    st.subheader("Quantitative Gains")
    roi_df = pd.DataFrame({
        "Task": ["Process Design", "User Story Writing", "Data Migration"],
        "Manual (Days)": [15, 7, 5],
        "AI-Assisted (Days)": [3, 0.5, 1]
    })
    st.table(roi_df)
    st.latex(r"ROI = \frac{(\text{Days Saved} \times \text{Daily Rate})}{\text{AI Subscription Cost}}")

# --- MODULE 2: AI CONSULTANT ---
elif choice == "🤖 AI Consultant":
    st.title("🤖 Virtual SPM Lead")
    if ai_ready:
        query = st.text_input("Ask about ServiceNow Best Practices:")
        if st.button("Generate Solution"):
            with st.spinner("Thinking..."):
                response = model.generate_content(f"Act as a ServiceNow SPM expert. Use CSDM 4.0. Query: {query}")
                st.markdown(response.text)
    else:
        st.error("Please provide an API Key to enable the Consultant.")

# --- MODULE 3: CSDM 4.0 AUDITOR ---
elif choice == "📋 CSDM 4.0 Auditor":
    st.title("📋 CSDM 4.0 Best Practice Auditor")
    mapping = st.text_area("Describe your CMDB/SPM table mapping:")
    if st.button("Run Audit"):
        if ai_ready:
            with st.spinner("Auditing..."):
                audit_prompt = f"Audit this for CSDM 4.0 alignment. Identify Red Flags: {mapping}"
                response = model.generate_content(audit_prompt)
                st.info("### Audit Results")
                st.markdown(response.text)
        else:
            st.error("AI not ready. Check API Key.")

# --- MODULE 4: DATA EXPLORER ---
elif choice == "📂 Data Explorer":
    st.title("📂 Sample Portfolio Data")
    if os.path.exists("spm_sample_data.csv"):
        df = pd.read_csv("spm_sample_data.csv")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Sample data (spm_sample_data.csv) not found in directory.")