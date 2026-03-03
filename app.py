import streamlit as st
import pandas as pd
import google.generativeai as genai
from fpdf import FPDF
from datetime import datetime
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="SNOW Agentic Pilot", page_icon="🤖", layout="wide")

# --- 🔐 API & MODEL SETUP ---
secret_key = st.secrets.get("GEMINI_API_KEY")
if secret_key:
    genai.configure(api_key=secret_key)
    # Using 'gemini-flash-latest' for 2026 stability
    model = genai.GenerativeModel('gemini-flash-latest')
    ai_ready = True
else:
    st.error("Missing GEMINI_API_KEY in Streamlit Secrets!")
    ai_ready = False

# --- 🧠 PERSISTENT STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "maturity" not in st.session_state:
    st.session_state.maturity = "Crawl"
if "active_agent" not in st.session_state:
    st.session_state.active_agent = "Orchestrator"

# --- 📄 COMPREHENSIVE ROADMAP GENERATOR ---
def generate_master_pdf(content, module_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(30, 41, 59) # Deep Slate
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_font("helvetica", 'B', 22)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 20, f"{module_name} Implementation Strategy", ln=True, align='C')
    pdf.set_font("helvetica", size=10)
    pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d')} | Confidentially Prepared", ln=True, align='C')
    
    pdf.set_y(50)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("helvetica", size=11)
    pdf.multi_cell(0, 8, content)
    return pdf.output()

# --- 🎨 UI & SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Implementation Control")
    st.session_state.maturity = st.select_slider("Implementation Maturity", options=["Legacy", "Crawl", "Walk", "Run", "Fly"])
    
    st.divider()
    st.subheader("Select Specialized Agent")
    agent_choice = st.radio("Active Expert:", ["Orchestrator", "SPM Specialist", "CSDM Architect", "CMDB Auditor", "SAMPro Consultant"])
    st.session_state.active_agent = agent_choice

    st.divider()
    if st.button("🏁 Generate 4-Phase Roadmap"):
        with st.spinner("Generating Detailed Project Plan..."):
            prompt = f"""Generate a detailed 4-phase implementation plan for {agent_choice}. 
            Phases: 1. Discovery, 2. Design/Build, 3. Validation/Change, 4. Production/Hypercare.
            Include: Team Structure, Roles (Architect, Owner, Lead), and Governance Model."""
            res = model.generate_content(prompt)
            st.session_state.roadmap_preview = res.text
            st.success("Plan Generated!")

# --- 🤖 MAIN INTERFACE ---
st.title(f"🚀 {st.session_state.active_agent} Dashboard")

# Agent-Specific Context Injection
agent_prompts = {
    "Orchestrator": "You are the Lead Project Orchestrator. Guide the user across all modules.",
    "SPM Specialist": "You are a ServiceNow SPM Expert. Focus on Strategic Planning and Value.",
    "CSDM Architect": "You are a CSDM 4.0 specialist. Focus on data modeling and domain mapping.",
    "CMDB Auditor": "You are a CMDB Quality Lead. Focus on data integrity and health.",
    "SAMPro Consultant": "You are a Software Asset Management Lead. Focus on license optimization."
}

# Chat Display
chat_container = st.container(height=450)
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

if prompt := st.chat_input(f"Consult with the {st.session_state.active_agent}..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_container:
        with st.chat_message("user"): st.markdown(prompt)
        
        if ai_ready:
            with st.chat_message("assistant"):
                system_instr = f"{agent_prompts[st.session_state.active_agent]} | Current Maturity: {st.session_state.maturity}. Be conversational."
                response = model.generate_content(f"{system_instr}\nUser: {prompt}")
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

# --- 📦 ONBOARDING & ROADMAP SECTION ---
col1, col2 = st.columns(2)
with col1:
    with st.expander("👤 New Employee Onboarding Hub"):
        st.write(f"Welcome to the {st.session_state.active_agent} team!")
        if st.button("Get My First 30 Days"):
            res = model.generate_content(f"Create a 30-day onboarding plan for a new consultant joining a {st.session_state.active_agent} project.")
            st.markdown(res.text)

with col2:
    if "roadmap_preview" in st.session_state:
        with st.expander("📄 Strategic Roadmap Preview"):
            st.markdown(st.session_state.roadmap_preview)
            pdf_bytes = generate_master_pdf(st.session_state.roadmap_preview, st.session_state.active_agent)
            st.download_button("📥 Download Final Implementation Plan", data=pdf_bytes, file_name="Roadmap.pdf")