import streamlit as st
import pandas as pd
import google.generativeai as genai
from fpdf import FPDF
from datetime import datetime
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="IC SURE HUB", page_icon="⚡", layout="wide")

# --- 🔐 API & MODEL ORCHESTRATION ---
# Logic to handle 2026 model discovery and prevent 404 errors
secret_key = st.secrets.get("GEMINI_API_KEY")
if secret_key:
    genai.configure(api_key=secret_key)
    try:
        # Dynamic discovery of the best available Flash model for 2026
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected_model = next((m for m in available_models if 'gemini-3' in m or 'flash' in m), "gemini-1.5-flash")
        model = genai.GenerativeModel(selected_model)
        ai_ready = True
    except Exception as e:
        st.error(f"AI Initialization Error: {e}")
        ai_ready = False
else:
    st.sidebar.error("🔑 API Key Missing in Secrets!")
    ai_ready = False

# --- 🧠 PERSISTENT STATE ---
agents = ["SPM", "CSDM", "CMDB", "SAMPro"]
if "history" not in st.session_state:
    st.session_state.history = {a: [] for a in agents}
if "plans" not in st.session_state:
    st.session_state.plans = {a: "" for a in agents}

# --- 📄 PDF ENGINE (Unicode Safe) ---
def create_pdf(content, title):
    # Sanitize characters for standard PDF fonts
    replacements = {"’": "'", "‘": "'", "“": '"', "”": '"', "—": "-", "–": "-", "…": "..."}
    for k, v in replacements.items(): content = content.replace(k, v)
    
    pdf = FPDF()
    pdf.add_page()
    # Header - IC SURE Branding
    pdf.set_fill_color(0, 80, 158) 
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_font("Helvetica", 'B', 18); pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 20, title, ln=True, align='C')
    pdf.set_y(50); pdf.set_text_color(0, 0, 0); pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 7, content)
    return pdf.output()

# --- 🎨 MAIN UI ---
st.title("⚡ IC SURE AI POWERED SERVICENOW TRANSFORMATION HUB")
st.caption("Strategic Digital Command Center for Oil & Gas Enterprise Transformation")

# --- SIDEBAR: EXECUTIVE STRATEGY ---
with st.sidebar:
    st.image("https://www.servicenow.com/content/dam/servicenow-assets/public/en-us/images/logos/servicenow-logo.png", width=150)
    st.header("🏢 Strategy Settings")
    maturity = st.select_slider("Org Maturity Level", ["Legacy", "Crawl", "Walk", "Run", "Fly"])
    st.info(f"Targeting: OT/IT Convergence & Asset Integrity")
    st.divider()
    if ai_ready:
        st.success(f"Brain Active: {selected_model}")

# --- SECTION 1: INDEPENDENT AGENT TABS ---
st.subheader("🤖 Specialized Transformation Agents")
tabs = st.tabs([f"📡 {a} Expert" for a in agents])

for i, agent in enumerate(agents):
    with tabs[i]:
        col_chat, col_tools = st.columns([2, 1])
        
        with col_chat:
            st.write(f"### {agent} Strategic Workstream")
            # Chat History
            for msg in st.session_state.history[agent]:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
            if user_input := st.chat_input(f"Consult {agent} Agent...", key=f"chat_{agent}"):
                st.session_state.history[agent].append({"role": "user", "content": user_input})
                with st.chat_message("user"): st.markdown(user_input)
                
                with st.chat_message("assistant"):
                    prompt = f"Act as a {agent} Consultant for Oil & Gas. Maturity: {maturity}. Include CSDM 4.0 context. Query: {user_input}"
                    response = model.generate_content(prompt).text
                    st.markdown(response)
                    st.session_state.history[agent].append({"role": "assistant", "content": response})

        with col_tools:
            st.button(f"🚩 Run Risk Audit", key=f"audit_{agent}", on_click=lambda