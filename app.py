import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="SPM AI Accelerator | ServiceNow",
    page_icon="🚀",
    layout="wide"
)

# --- STYLE CUSTOMIZATION ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# --- API KEY & MODEL SETUP ---
# Priority: 1. Streamlit Secrets -> 2. Manual Sidebar Input
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Gemini API Key", type="password", help="Get a free key at aistudio.google.com")

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        ai_ready = True
    except Exception as e:
        st.error(f"API Configuration Error: {e}")
        ai_ready = False
else:
    st.sidebar.warning("⚠️ API Key missing. Add it to Streamlit Secrets or enter it above to enable AI features.")
    ai_ready = False

# --- NAVIGATION ---
st.sidebar.title("Navigation")
menu = ["📊 Value Dashboard", "🤖 AI Consultant", "🎓 Onboarding Hub", "📂 Data Explorer"]
choice = st.sidebar.radio("Go to", menu)

# --- MODULE 1: VALUE DASHBOARD (The "Sales" Pitch) ---
if choice == "📊 Value Dashboard":
    st.title("🚀 SPM Implementation Accelerator")
    st.subheader("Quantitative Benefits & ROI")
    
    # Key Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Implementation Speed", "4x Faster", "80% Reduction")
    m2.metric("Story Quality Score", "98%", "+25% vs Manual")
    m3.metric("Estimated Cost Savings", "$22,500