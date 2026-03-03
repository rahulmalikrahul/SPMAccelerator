import streamlit as st
import pandas as pd
import google.generativeai as genai
from fpdf import FPDF
from datetime import datetime
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="IC SURE HUB", page_icon="⚡", layout="wide")

# --- 🔐 API SETUP ---
secret_key = st.secrets.get("GEMINI_API_KEY")
if secret_key:
    genai.configure(api_key=secret_key)
    model = genai.GenerativeModel('gemini-flash-latest')
    ai_ready = True
else:
    st.error("Missing GEMINI_API_KEY in Secrets!")
    ai_ready = False

# --- 🧠 SESSION STATE ---
agents = ["SPM", "CSDM", "CMDB", "SAMPro"]
if "history" not in st.session_state:
    st.session_state.history = {a: [] for a in agents}
if "plans" not in st.session_state:
    st.session_state.plans = {a: "" for a in agents}

# --- 📄 PDF GENERATOR ---
def create_pdf(content, title):
    replacements = {"’": "'", "‘": "'", "“": '"', "”": '"', "—": "-", "–": "-"}
    for k, v in replacements.items(): content = content.replace(k, v)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(13, 148, 136) # IC SURE Teal
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_font("Helvetica", 'B', 16); pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 20, title, ln=True, align='C')
    pdf.set_y(50); pdf.set_text_color(0, 0, 0); pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 7, content)
    return pdf.output()

# --- 🎨 UI LAYOUT ---
st.title("⚡ IC SURE AI POWERED SERVICENOW TRANSFORMATION HUB")
st.markdown("---")

# Global Sidebar
with st.sidebar:
    st.header("🏢 Enterprise Strategy")
    maturity = st.select_slider("Maturity Level", ["Legacy", "Crawl", "Walk", "Run", "Fly"])
    st.divider()
    st.info("Relevance: Oil & Gas Operations (Upstream/Downstream)")

# --- MAIN AGENT TABS ---
tabs = st.tabs([f"🚀 {a} Expert" for a in agents])

for i, agent in enumerate(agents):
    with tabs[i]:
        col_chat, col_tools = st.columns([2, 1])
        
        with col_chat:
            st.subheader(f"{agent} Module Intelligence")
            for msg in st.session_state.history[agent]:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
            if user_input := st.chat_input(f"Consult {agent} Agent...", key=f"input_{agent}"):
                st.session_state.history[agent].append({"role": "user", "content": user_input})
                with st.chat_message("user"): st.markdown(user_input)
                
                with st.chat_message("assistant"):
                    prompt = f"Agent: {agent} Expert for Oil & Gas. Maturity: {maturity}. Context: Implementation methodology, roles (Architect, PMO, Change Lead), and governance. Query: {user_input}"
                    response = model.generate_content(prompt).text
                    st.markdown(response)
                    st.session_state.history[agent].append({"role": "assistant", "content": response})

        with col_tools:
            st.subheader("🚩 Risk Auditor")
            if st.button(f"Audit {agent} Risks", key=f"audit_{agent}"):
                audit_res = model.generate_content(f"Identify 3 Oil & Gas specific Red Flags for {agent} at {maturity} maturity.").text
                st.error(audit_res)
            
            st.divider()
            st.subheader("📋 Project Artifacts")
            if st.button(f"Generate {agent} Project Plan", key=f"plan_{agent}"):
                plan_prompt = f"Build end-to-end Project Plan for {agent} in Oil & Gas. Phases: Discovery, Design/Build, Validation, Hypercare. Include Roles: Architect, PMO, Change Management."
                st.session_state.plans[agent] = model.generate_content(plan_prompt).text
                st.success("Plan Generated!")

            if st.session_state.plans[agent]:
                st.download_button("📥 One-Page Summary", create_pdf(st.session_state.plans[agent][:1200], f"{agent} Executive View"), f"{agent}_OnePager.pdf")
                st.download_button("📥 Detailed Roadmap", create_pdf(st.session_state.plans[agent], f"{agent} Detailed Plan"), f"{agent}_Detailed.pdf")

# --- NEW SECTION: ROLE-BASED EXECUTION ENGINE ---
st.markdown("---")
st.header("🛠️ Role-Based Execution Engine")
st.write("Select your specific role and phase to receive step-by-step technical and process guidance.")

role_col, stage_col, module_col = st.columns(3)

with role_col:
    exec_role = st.selectbox("Your Project Role", ["Implementation Architect", "PMO Lead", "Change Management Lead", "Business Analyst"])

with stage_col:
    exec_stage = st.selectbox("Project Stage", ["Design (Requirements/Solutioning)", "Build (Configuration/Unit Testing)", "Deploy (Validation/UAT/Hypercare)"])

with module_col:
    exec_module = st.selectbox("Focus Module", agents)

if st.button("🚀 Get My Action Plan"):
    if ai_ready:
        with st.spinner("Calculating Step-by-Step Instructions..."):
            exec_prompt = f"""
            Act as an IC SURE Transformation Lead.
            Role: {exec_role}
            Stage: {exec_stage}
            Module: {exec_module}
            Industry: Oil & Gas
            
            Provide a detailed 1-2-3 step-by-step guidance for this specific combination. 
            Include an 'Industry Example' for each step (e.g., related to drilling rigs, offshore assets, or seismic software).
            Include specific PMO/Change tasks if those roles are selected.
            """
            exec_response = model.generate_content(exec_prompt).text
            st.success(f"Action Plan for {exec_role} - {exec_stage}")
            st.markdown(exec_response)
    else:
        st.error("AI Key required for this section.")

# --- FOOTER ---
st.markdown("---")
with st.expander("👤 New Hire Onboarding Pop-up"):
    new_role = st.selectbox("Onboarding Role", ["PMO", "Change Manager", "Technical Consultant"])
    if st.button("Start Induction"):
        onboard = model.generate_content(f"30-day onboarding for a {new_role} in an Oil & Gas ServiceNow project.").text
        st.info(onboard)