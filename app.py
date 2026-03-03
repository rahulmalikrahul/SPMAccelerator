import streamlit as st
import pandas as pd
import google.generativeai as genai
from fpdf import FPDF
from datetime import datetime
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="IC SURE HUB", page_icon="⚡", layout="wide")

# --- 🔐 API & MODEL ORCHESTRATION ---
secret_key = st.secrets.get("GEMINI_API_KEY")
if secret_key:
    genai.configure(api_key=secret_key)
    try:
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

# --- 📄 PDF ENGINE ---
def create_pdf(content, title):
    replacements = {"’": "'", "‘": "'", "“": '"', "”": '"', "—": "-", "–": "-", "…": "..."}
    for k, v in replacements.items(): content = content.replace(k, v)
    pdf = FPDF()
    pdf.add_page()
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

# --- SIDEBAR ---
with st.sidebar:
    st.header("🏢 Strategy Settings")
    maturity = st.select_slider("Org Maturity Level", ["Legacy", "Crawl", "Walk", "Run", "Fly"])
    st.info("Industry Context: Oil & Gas Operations")
    if ai_ready: st.success(f"Brain: {selected_model}")

# --- SECTION 1: AGENT TABS ---
tabs = st.tabs([f"📡 {a} Expert" for a in agents])

for i, agent in enumerate(agents):
    with tabs[i]:
        col_chat, col_tools = st.columns([2, 1])
        
        with col_chat:
            st.write(f"### {agent} Strategic Workstream")
            for msg in st.session_state.history[agent]:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
            # Using unique keys for each chat input to avoid conflicts
            if user_input := st.chat_input(f"Consult {agent}...", key=f"chat_input_{agent}"):
                st.session_state.history[agent].append({"role": "user", "content": user_input})
                with st.chat_message("user"): st.markdown(user_input)
                
                with st.chat_message("assistant"):
                    prompt = f"Agent: {agent} Specialist for Oil & Gas. Maturity: {maturity}. Query: {user_input}"
                    response = model.generate_content(prompt).text
                    st.markdown(response)
                    st.session_state.history[agent].append({"role": "assistant", "content": response})

        with col_tools:
            st.subheader("🚩 Risk Auditor")
            if st.button(f"Run {agent} Risk Audit", key=f"audit_btn_{agent}"):
                with st.spinner("Analyzing Risks..."):
                    audit_res = model.generate_content(f"3 Oil & Gas Red Flags for {agent} at {maturity} maturity.").text
                    st.error(audit_res)
            
            st.divider()
            st.subheader("📋 Project Artifacts")
            if st.button(f"Generate {agent} Roadmap", key=f"gen_plan_{agent}"):
                with st.spinner("Drafting..."):
                    res = model.generate_content(f"4-phase Plan for {agent} in O&G. Include Roles: PMO, Architect, Change Mgmt.").text
                    st.session_state.plans[agent] = res
                    st.success("Plan Ready")
            
            if st.session_state.plans[agent]:
                st.download_button("📥 Summary (PDF)", create_pdf(st.session_state.plans[agent][:1200], f"{agent} Summary"), f"{agent}_OnePager.pdf", key=f"dl_short_{agent}")
                st.download_button("📥 Roadmap (PDF)", create_pdf(st.session_state.plans[agent], f"{agent} Detailed"), f"{agent}_Detailed.pdf", key=f"dl_full_{agent}")

# --- SECTION 2: ROLE-BASED EXECUTION ENGINE ---
st.divider()
st.header("⚙️ Role-Based Execution Engine")
r_col, s_col, m_col = st.columns(3)
with r_col: exec_role = st.selectbox("Your Role", ["Implementation Architect", "PMO Lead", "Change Management Lead", "Business Analyst"])
with s_col: exec_stage = st.selectbox("Current Stage", ["Design (Requirements)", "Build (Config)", "Deploy (Validation)"])
with m_col: exec_mod = st.selectbox("Module Under Implementation", agents)

if st.button("🚀 Get My Action Plan", key="exec_btn"):
    with st.spinner("Calculating..."):
        instr = model.generate_content(f"Role: {exec_role}, Stage: {exec_stage}, Module: {exec_mod}. Step-by-step O&G guide with examples.").text
        st.info(instr)

# --- SECTION 3: TECHNICAL CONFIG & OOTB REVIEW ---
st.divider()
st.header("🛠️ Technical Config & OOTB Mapping Engine")
c1, c2 = st.columns([2,1])
with c1: 
    config_desc = st.