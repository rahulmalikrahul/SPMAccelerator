import streamlit as st
import pandas as pd
import google.generativeai as genai
from fpdf import FPDF
from datetime import datetime
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="EnergyOps Agentic Pilot", page_icon="🛢️", layout="wide")

# --- 🔐 API SETUP ---
secret_key = st.secrets.get("GEMINI_API_KEY")
if secret_key:
    genai.configure(api_key=secret_key)
    model = genai.GenerativeModel('gemini-flash-latest')
    ai_ready = True
else:
    st.error("Missing GEMINI_API_KEY in Secrets!")
    ai_ready = False

# --- 🧠 SESSION STATE INITIALIZATION ---
agents = ["SPM", "CSDM", "CMDB", "SAMPro"]
if "history" not in st.session_state:
    st.session_state.history = {a: [] for a in agents}
if "plans" not in st.session_state:
    st.session_state.plans = {a: "" for a in agents}

# --- 📄 PDF GENERATOR ---
def create_pdf(content, title):
    # Sanitize content for Latin-1
    replacements = {"’": "'", "‘": "'", "“": '"', "”": '"', "—": "-", "–": "-"}
    for k, v in replacements.items(): content = content.replace(k, v)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(0, 50, 100) # Oil & Gas Deep Blue
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_font("Helvetica", 'B', 18); pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 20, title, ln=True, align='C')
    pdf.set_y(50); pdf.set_text_color(0, 0, 0); pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 7, content)
    return pdf.output()

# --- 🛠️ AGENT LOGIC ---
def run_agent_workflow(agent_name, user_input, maturity):
    role_map = {
        "SPM": "Expert in Capital Project Management and Demand for Energy.",
        "CSDM": "Enterprise Architect specializing in OT/IT convergence (CSDM 4.0).",
        "CMDB": "Data Quality Lead for complex Industrial CMDB (OT & IT).",
        "SAMPro": "Licensing Specialist for high-cost Engineering & Seismic software."
    }
    
    prompt = f"""
    Agent: {agent_name} Specialist ({role_map[agent_name]})
    Context: Oil & Gas Sector.
    Current Maturity: {maturity}.
    Phases: Discovery, Design/Build, Validation, Production.
    
    User Query: {user_input}
    
    Instruction: Provide a response that guides them through the current phase, 
    identifying red flags specific to Oil & Gas (e.g. safety regs, remote asset discovery).
    """
    return model.generate_content(prompt).text

# --- 🎨 UI LAYOUT ---
st.title("🛢️ EnergyOps Strategic Command Center")
st.caption("2026 Enterprise ServiceNow Pilot for Oil & Gas")

maturity = st.sidebar.select_slider("Select Organization Maturity", ["Legacy", "Crawl", "Walk", "Run", "Fly"])

# TABS FOR INDEPENDENT AGENTS
tabs = st.tabs([f"🛡️ {a} Agent" for a in agents])

for i, agent in enumerate(agents):
    with tabs[i]:
        col_chat, col_audit = st.columns([2, 1])
        
        with col_chat:
            st.subheader(f"{agent} Implementation Pilot")
            # Chat History
            for msg in st.session_state.history[agent]:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
            if user_input := st.chat_input(f"Consult {agent} Expert...", key=f"input_{agent}"):
                st.session_state.history[agent].append({"role": "user", "content": user_input})
                with st.chat_message("user"): st.markdown(user_input)
                
                with st.chat_message("assistant"):
                    response = run_agent_workflow(agent, user_input, maturity)
                    st.markdown(response)
                    st.session_state.history[agent].append({"role": "assistant", "content": response})

        with col_audit:
            st.subheader("🚩 Auditor Red Flags")
            if st.button(f"Audit {agent} Strategy", key=f"audit_btn_{agent}"):
                with st.spinner("Analyzing Risks..."):
                    audit_res = model.generate_content(f"Perform a risk audit for an Oil & Gas {agent} project at {maturity} maturity. Identify 3 specific red flags.").text
                    st.error(audit_res)

            st.divider()
            if st.button(f"📅 Build {agent} Project Plan", key=f"plan_{agent}"):
                with st.spinner("Drafting Phased Roadmap..."):
                    plan_prompt = f"Generate a 4-phase project plan for {agent} in Oil & Gas. Include Team Structure (Architect, Lead, BA), Operating Model, and Roles & Responsibilities."
                    st.session_state.plans[agent] = model.generate_content(plan_prompt).text
                    st.success("Plan Generated!")

            if st.session_state.plans[agent]:
                st.download_button("📥 One-Page Strategy (PDF)", 
                                   create_pdf(st.session_state.plans[agent][:1500], f"{agent} Executive Summary"), 
                                   f"{agent}_OnePager.pdf")
                st.download_button("📥 Full Project Plan (PDF)", 
                                   create_pdf(st.session_state.plans[agent], f"{agent} Detailed Roadmap"), 
                                   f"{agent}_DetailedPlan.pdf")

# --- 👤 ONBOARDING POP-UP SIMULATION ---
with st.expander("👋 Consultant Onboarding Hub", expanded=False):
    st.write("New to the EnergyOps project? Get your induction plan here.")
    role = st.selectbox("Your Role", ["Implementation Lead", "Process Architect", "Business Analyst"])
    if st.button("Generate Onboarding Guide"):
        onboard_res = model.generate_content(f"Create a 30-day onboarding plan for a {role} on an Oil & Gas ServiceNow project.").text
        st.info(onboard_res)