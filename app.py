import streamlit as st
import pandas as pd
import google.generativeai as genai
from fpdf import FPDF
import io
from datetime import datetime

# --- 🎨 UI THEME CONFIGURATION ---
st.set_page_config(page_title="ServiceNow AI Transformation", page_icon="⚡", layout="wide")

# [cite_start]Custom CSS for the Blue/Black/White Premium Look [cite: 1]
st.markdown("""
    <style>
    .main { background-color: #ffffff; color: #1a1a1a; }
    .stApp { background-color: #ffffff; }
    h1, h2, h3 { color: #00509d !important; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    .stButton>button { 
        background-color: #00509d; color: white; border-radius: 5px; 
        border: none; font-weight: bold; width: 100%;
    }
    .stButton>button:hover { background-color: #003d7a; border: none; color: white; }
    .stExpander { border: 1px solid #00509d; border-radius: 5px; }
    .stSidebar { background-color: #f8f9fa; border-right: 2px solid #00509d; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6; border-radius: 5px 5px 0px 0px;
        padding: 10px 20px; color: #1a1a1a;
    }
    .stTabs [aria-selected="true"] { background-color: #00509d !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🔐 API & MODEL SETUP ---
secret_key = st.secrets.get("GEMINI_API_KEY")
if secret_key:
    genai.configure(api_key=secret_key)
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected_model = next((m for m in available_models if 'flash' in m), "gemini-1.5-flash")
        model = genai.GenerativeModel(selected_model)
        ai_ready = True
    except:
        ai_ready = False
else:
    st.sidebar.error("🔑 API Key Missing")
    ai_ready = False

# --- 🧠 SESSION STATE ---
modules = ["SPM", "CSDM", "CMDB", "SAMPro", "ITSM"]
if "history" not in st.session_state:
    st.session_state.history = {m: [] for m in modules}
if "plans" not in st.session_state:
    st.session_state.plans = {m: "" for m in modules}

# --- 🛠️ HELPER FUNCTIONS ---
def sanitize(text):
    return text.encode('latin-1', 'replace').decode('latin-1').replace('?', "'")

def create_pdf(content, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(0, 80, 157) # ServiceNow Blue
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_font("Helvetica", 'B', 20); pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 20, sanitize(title), ln=True, align='C')
    pdf.set_y(50); pdf.set_text_color(0, 0, 0); pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 7, sanitize(content))
    # FIX: Explicitly cast bytearray to bytes to resolve StreamlitAPIException
    [cite_start]return bytes(pdf.output()) [cite: 1]

def create_excel(content, sheet_name):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    lines = content.split('\n')
    df = pd.DataFrame(lines, columns=[f"{sheet_name} Technical Details"])
    df.to_excel(writer, index=False, sheet_name=sheet_name)
    writer.close()
    [cite_start]return output.getvalue() [cite: 1]

# --- 🏗️ SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🛡️ Global Settings")
    industry = st.selectbox("Industry Focus", ["Oil & Gas / OT-IT Convergence", "Mining", "Oil Field Services", "Utilities", "Manufacturing", "Public Sector"])
    maturity = st.select_slider("Maturity Level", ["Legacy", "Crawl", "Walk", "Run", "Fly"])
    st.divider()
    st.write(f"**Industry:** {industry}")
    st.write(f"**Maturity:** {maturity}")

# --- 🚀 HEADER ---
st.title("⚡ AI POWERED SERVICENOW TRANSFORMATION")
st.markdown(f"**Strategic Intelligent Orchestrator for {industry}**")

# --- SECTION 1: MODULE AGENTS ---
tabs = st.tabs([f"🔹 {m}" for m in modules])

for i, m_name in enumerate(modules):
    with tabs[i]:
        col_chat, col_tools = st.columns([2, 1])
        
        with col_chat:
            st.subheader(f"{m_name} Cognitive Agent")
            for msg in st.session_state.history[m_name]:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
            if user_input := st.chat_input(f"Consult {m_name} Specialist...", key=f"chat_{m_name}"):
                st.session_state.history[m_name].append({"role": "user", "content": user_input})
                with st.chat_message("user"): st.markdown(user_input)
                
                with st.chat_message("assistant"):
                    prompt = f"Agent: {m_name} Expert for {industry}. Maturity: {maturity}. Context: Implementation, Governance, Technical Debt. User Query: {user_input}"
                    response = model.generate_content(prompt).text
                    st.markdown(response)
                    st.session_state.history[m_name].append({"role": "assistant", "content": response})

        with col_tools:
            st.subheader("🚩 Project Auditor")
            if st.button(f"Scan {m_name} Risks", key=f"audit_{m_name}"):
                res = model.generate_content(f"3 industry-specific red flags for {m_name} in {industry} at {maturity} maturity.").text
                st.error(res)
            
            st.divider()
            st.subheader("📋 Artifacts")
            if st.button(f"Build {m_name} Roadmap", key=f"plan_{m_name}"):
                res = model.generate_content(f"Create 4-phase Roadmap for {m_name} in {industry}. Roles: Architect, PMO, Change Mgmt.").text
                st.session_state.plans[m_name] = res
                st.success("Roadmap Ready")
            
            if st.session_state.plans[m_name]:
                st.download_button("📥 Download One-Pager (PDF)", create_pdf(st.session_state.plans[m_name][:1500], f"{m_name} Strategy"), f"{m_name}_OnePager.pdf", key=f"dl_p_{m_name}")

# --- SECTION 2: ROLE-BASED EXECUTION ---
st.divider()
st.header("⚙️ Role-Based Execution Engine")
r_col, s_col, m_col = st.columns(3)
with r_col: exec_role = st.selectbox("Your Role", ["Implementation Architect", "Process Architect", "PMO Lead", "Change Management Lead", "Business Analyst", "Technical Lead"])
with s_col: exec_stage = st.selectbox("Current Phase", ["Design (Requirements)", "Build (Config)", "Deploy (Validation)"])
with m_col: exec_mod = st.selectbox("Module Selection", modules)

if st.button("🚀 Generate Action Plan", key="exec_btn"):
    res = model.generate_content(f"Provide detailed step-by-step guidance for {exec_role} in the {exec_stage} phase of {exec_mod} for {industry}.").text
    st.info(res)

# --- SECTION 3: TECHNICAL MAPPING ---
st.divider()
st.header("🛠️ Technical Mapping Generator")
mapping_input = st.text_area("Describe the Technical Requirements (e.g., 'Map Mining Haul Truck sensors to CMDB'):", height=100)
if st.button("📝 Generate Technical Mapping", key="map_btn"):
    with st.spinner("Generating..."):
        map_res = model.generate_content(f"Create technical mapping sheet and update set naming for: {mapping_input} in {exec_mod} for {industry}.").text
        st.session_state.mapping_data = map_res
        st.code(map_res, language="markdown")

if "mapping_data" in st.session_state:
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("📥 Download Mapping (PDF)", create_pdf(st.session_state.mapping_data, "Technical Mapping"), "Mapping.pdf")
    with c2:
        st.download_button("📥 Download Mapping (Excel)", create_excel(st.session_state.mapping_data, "Mapping"), "Mapping.xlsx")

# --- SECTION 4: OOTB BEST PRACTICE REVIEW ---
st.divider()
st.header("⚖️ OOTB Best Practice Review")
review_input = st.text_area("Paste Configuration Plan for OOTB Audit:", height=100, key="ootb_input")
if st.button("🔍 Run OOTB Review", key="rev_btn"):
    res = model.generate_content(f"Review this {exec_mod} config for OOTB compliance in {industry}: {review_input}. Identify customization traps.").text
    st.warning(res)

# --- SECTION 5: NEW HIRE INDUCTION ---
st.divider()
st.header("👤 New Hire Induction Hub")
on_role = st.selectbox("Onboarding Role", ["PMO", "Change Manager", "Technical Lead", "Implementation Architect", "Process Architect", "Business Analyst", "Business User"])
if st.button("🏁 Start 30-Day Induction"):
    res = model.generate_content(f"Create a 30-day induction plan for a {on_role} on a {exec_mod} project in the {industry} sector.").text
    st.markdown(res)