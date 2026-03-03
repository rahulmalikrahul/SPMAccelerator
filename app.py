import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="SPM AI Accelerator",
    page_icon="🚀",
    layout="wide"
)

# --- STYLE ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #007bff; }
    </style>
    """, unsafe_allow_html=True)

# --- API KEY & MODEL SETUP ---
# It will first look for the key in Streamlit Secrets (for Cloud deployment)
# If not found, it provides a sidebar input (for local testing)
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        ai_ready = True
    except Exception as e:
        st.sidebar.error(f"Error: {e}")
        ai_ready = False
else:
    st.sidebar.warning("🔑 Enter API Key to enable AI Features")
    ai_ready = False

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("SPM AI Navigator")
menu = ["Value Dashboard", "AI Consultant", "Onboarding Hub", "Data Explorer"]
choice = st.sidebar.radio("Modules", menu)

# --- MODULE 1: VALUE DASHBOARD ---
if choice == "Value Dashboard":
    st.title("📈 Implementation Value Realization")
    st.markdown("Comparing traditional ServiceNow SPM implementation vs. AI-Accelerated delivery.")
    
    # Corrected Metrics Section
    m1, m2, m3 = st.columns(3)
    m1.metric("Delivery Speed", "4.5x Faster", "82% Improvement")
    m2.metric("Documentation Quality", "High", "OOTB Aligned")
    m3.metric("Projected Savings", "$22,500", "Per Lifecycle")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Quantitative Benefits")
        roi_data = {
            "Implementation Task": ["Process Design", "User Story Writing", "Test Scripting", "Data Load"],
            "Manual (Days)": [15, 7, 10, 5],
            "AI-Assisted (Days)": [3, 0.5, 2, 1]
        }
        st.table(pd.DataFrame(roi_data))
    
    with col2:
        st.subheader("The ROI Formula")
        st.write("We calculate implementation value using the following model:")
        st.latex(r"ROI = \frac{(\text{Manual Hours} - \text{AI Hours}) \times \text{Hourly Rate}}{\text{Tool Investment}}")
        st.info("💡 By automating documentation, we reduce 'Implementation Fatigue' by 60%.")

# --- MODULE 2: AI CONSULTANT ---
elif choice == "AI Consultant":
    st.title("🤖 Virtual SPM Lead")
    st.write("Get expert guidance on ServiceNow Best Practices (Demand, Project, Resource, Portfolio).")

    if ai_ready:
        query = st.text_input("Ask a question (e.g., 'What are the mandatory fields for Demand screening?'):")
        if st.button("Generate Solution"):
            with st.spinner("Consulting AI..."):
                prompt = f"Act as a ServiceNow SPM expert. Use CSDM 4.0 standards. Answer this: {query}"
                response = model.generate_content(prompt)
                st.markdown("---")
                st.markdown(response.text)
    else:
        st.error("API Key required for this module.")

# --- MODULE 3: ONBOARDING HUB ---
elif choice == "Onboarding Hub":
    st.title("🎓 Consultant Training")
    st.write("Onboard new consultants by testing their knowledge on SPM best practices.")
    
    scenario = "Stakeholder A wants to track Project costs in a separate Excel sheet instead of ServiceNow. How do you advise them?"
    st.info(f"**Current Scenario:** {scenario}")
    
    ans = st.text_area("Your response as a consultant:")
    if st.button("Evaluate Response"):
        if ai_ready:
            with st.spinner("Grading..."):
                eval_prompt = f"Rate this consultant's answer based on ServiceNow SPM best practices. Scenario: {scenario}. Answer: {ans}"
                res = model.generate_content(eval_prompt)
                st.success("Expert Feedback:")
                st.write(res.text)
        else:
            st.error("API Key required for evaluation.")

# --- MODULE 4: DATA EXPLORER ---
elif choice == "Data Explorer":
    st.title("📂 Sample Project Portfolio")
    
    if os.path.exists("spm_sample_data.csv"):
        df = pd.read_csv("spm_sample_data.csv")
        st.dataframe(df, use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.write("### Portfolios by Count")
            st.bar_chart(df["Portfolio"].value_counts())
        with c2:
            st.write("### Planned vs Actual Cost")
            st.line_chart(df[["Planned Cost ($)", "Actual Cost ($)"]])
    else:
        st.warning("No data found. Please run the data_generator.py script first.")

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.caption("ServiceNow SPM AI Pilot v1.0")