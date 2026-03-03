import streamlit as st
import pandas as pd
import google.generativeai as genai
from fpdf import FPDF
import io
import xlsxwriter
from datetime import datetime

# --- 🎨 ACCELQ-INSPIRED UI THEME ---
st.set_page_config(page_title="SNOW AI Transformation", page_icon="🌐", layout="wide")

# Custom CSS for the "Dark Tech" Aesthetic
st.markdown("""
    <style>
    /* Main Background & Text */
    .stApp {
        background: radial-gradient(circle at top right, #001a3d, #00041c);
        color: #ffffff;
    }
    
    /* Headers & Cyan Accents */
    h1, h2, h3 {
        color: #00f5ff !important;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #000b2e !important;
        border-right: 2px solid #00f5ff;
    }
    
    /* Button Styling - Glowing Cyan */
    .stButton>button {
        background-color: #00f5ff !important;
        color: #00041c !important;
        border-radius: 2px !important;
        border: none !important;
        font-weight: 800 !important;
        transition: 0.3s all ease;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        box-shadow: 0 0 15px #00f5ff;
        transform: translateY(-2px);
    }
    
    /* Chat & Container Styling */
    [data-testid="stChatMessage"] {
        background-color: #001233 !important;
        border: 1px solid #00f5ff33;
        border-radius: 10px;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent;
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #001233;
        border: 1px solid #00f5ff33;
        color: #ffffff !important;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00f5ff !important;
        color: #00041c !important;
    }

    /* Expander/Cards */
    .stExpander {
        background-color: #001233 !important;
        border: 1px solid #00f5ff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🔐 API & MODEL INITIALIZATION ---
secret_key = st.secrets.get("GEMINI_API_KEY")
if secret_key:
    genai.configure(api_key=secret_key)
    try:
        # Dynamic discovery for 2026 models
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected_model = next((m for m in available_models if 'flash' in m), "gemini-1.5-flash")
        model = genai.GenerativeModel(selected_model)
        ai_ready = True
    except: ai_ready = False
else:
    st.sidebar.warning("📡 SYSTEM OFFLINE: Key Required")
    ai_ready = False

# --- 🧠 STATE MANAGEMENT ---
modules = ["SPM", "CSDM", "CMDB", "SAMPro", "ITSM"]
if "history" not in st.session_state:
    st.session_state.history = {m: [] for m in modules}
if "plans" not in st.session_state:
    st.session_state.plans = {m: "" for m in modules}
if "tech_map" not in st.session_state:
    st.session_state.tech_map = ""

# --- 📄 EXPORT UTILITIES ---
def create_pdf(content, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(0, 4, 28) # Dark Navy
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_font("Helvetica", 'B', 18); pdf.set_text_color(0, 245, 255) # Cyan
    pdf.cell(0, 20, title.encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')
    pdf.set_y(50); pdf.set_text_color(0, 0, 0); pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 7, content.encode('latin-1', 'replace').decode('latin-1'))
    return pdf.output()

def create_excel(content, sheet_name):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    wrap_format = workbook.add_format({'text_wrap': True, 'valign': 'top'})
    worksheet.write('A1', f'{sheet_name} Content', workbook.add_format({'bold': True, 'bg_color': '#00f5ff'}))
    worksheet.write('A2', content, wrap_format)
    worksheet.set_column('A:A', 100)
    workbook.close()
    return output.getvalue()

# --- 🏗️ SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h2 style='color:#00f5ff;'>CORE CONTROL</h2>", unsafe_allow_html=True)
    industry = st.selectbox("INDUSTRY FOCUS", ["Oil & Gas / OT-IT Convergence", "Mining", "Oil Field Services", "Utilities", "Manufacturing", "Financial Services"])
    maturity = st.select_slider("MATURITY LEVEL", ["Legacy", "Crawl", "Walk", "Run", "Fly"])
    st.divider()
    if ai_ready: st.success("✅ AI AGENTS LINKED")

# --- ⚡ MAIN HUB ---
st.title("⚡ AI POWERED SERVICENOW TRANSFORMATION")
st.caption(f"Intelligent Orchestration Engine | Sector: {industry} | Strategy: {maturity}")

# --- SECTION 1: TRANSFORMATION AGENTS ---
tabs = st.tabs([f"💠 {m}" for m in modules])

for i, m_name in enumerate(modules):
    with tabs[i]:
        col_chat, col_tools = st.columns([2, 1])
        
        with col_chat:
            st.markdown(f"### {m_name} COGNITIVE WORKSTREAM")
            for msg in st.session_state.history[m_name]:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
            if user_input := st.chat_input(f"Consult {m_name} Pilot...", key=f"chat_{m_name}"):
                st.session_state.history[m_name].append({"role": "user", "content": user_input})
                with st.chat_message("user"): st.markdown(user_input)
                
                with st.chat_message("assistant"):
                    prompt = f"Act as a {m_name} Agent for {industry}. Maturity: {maturity}. Provide specific strategic advice for: {user_input}"
                    response = model.generate_content(prompt).text
                    st.markdown(response)
                    st.session_state.history[m_name].append({"role": "assistant", "content": response})

        with col_tools:
            st.markdown("### 🔍 RISK AUDIT")
            if st.button(f"SCAN {m_name} ANOMALIES", key=f"audit_{m_name}"):
                res = model.generate_content(f"Perform a risk audit for {m_name} in {industry}. Identify 3 industry-specific red flags.").text
                st.error(res)
            
            st.divider()
            st.markdown("### 📋 STRATEGIC ARTIFACTS")
            if st.button(f"BUILD {m_name} ROADMAP", key=f"plan_{m_name}"):
                res = model.generate_content(f"Create a 4-phase implementation roadmap for {m_name} in {industry}. Include PMO and Change Management logic.").text
                st.session_state.plans[m_name] = res
                st.success("Roadmap Sync Complete")
            
            if st.session_state.plans[m_name]:
                st.download_button("📥 DOWNLOAD PDF", create_pdf(st.session_state.plans[m_name], f"{m_name} Plan"), f"{m_name}_Strategy.pdf", key=f"dl_pdf_{m_name}")

# --- SECTION 2: ROLE-BASED EXECUTION ENGINE ---
st.markdown("---")
st.header("⚙️ ROLE-BASED EXECUTION ENGINE")
r_col, s_col, m_col = st.columns(3)
with r_col: e_role = st.selectbox("PROJECT ROLE", ["Implementation Architect", "Process Architect", "Technical Lead", "PMO Lead", "Change Management Lead", "Business Analyst"])
with s_col: e_stage = st.selectbox("CURRENT PHASE", ["Design (Requirements)", "Build (Config)", "Deploy (Validation)"])
with m_col: e_mod = st.selectbox("MODULE CONTEXT", modules, key="exec_mod")

if st.button("🚀 GENERATE EXECUTION STEPS", key="exec_btn"):
    res = model.generate_content(f"Detailed instructions for {e_role} during {e_stage} phase of {e_mod} in {industry}. Provide technical and process steps.").text
    st.info(res)

# --- SECTION 3: TECHNICAL MAPPING GENERATOR ---
st.markdown("---")
st.header("🛠️ TECHNICAL CONFIGURATION MAPPING")
mapping_desc = st.text_area("DESCRIBE TECHNICAL REQUIREMENTS (e.g. Asset CI Mapping or Discovery Patterns):", height=100)
if st.button("📝 GENERATE MAPPING SHEET", key="map_btn"):
    with st.spinner("Processing Logic..."):
        st.session_state.tech_map = model.generate_content(f"Create a technical configuration mapping sheet and update set strategy for {mapping_desc} in {e_mod} for {industry}.").text
        st.code(st.session_state.tech_map, language="markdown")

if st.session_state.tech_map:
    pdf_col, xls_col = st.columns(2)
    with pdf_col:
        st.download_button("📥 DOWNLOAD MAPPING (PDF)", create_pdf(st.session_state.tech_map, "Technical Mapping"), "Mapping.pdf")
    with xls_col:
        st.download_button("📥 DOWNLOAD MAPPING (EXCEL)", create_excel(st.session_state.tech_map, "Technical_Mapping"), "Mapping.xlsx")

# --- SECTION 4: OOTB BEST PRACTICE REVIEW ---
st.markdown("---")
st.header("⚖️ OOTB BEST PRACTICE REVIEW")
config_data = st.text_area("PASTE CONFIGURATION PLAN FOR AUDIT:", height=100, key="ootb_area")
if st.button("🔍 RUN OOTB COMPLIANCE CHECK", key="ootb_btn"):
    res = model.generate_content(f"Audit this {e_mod} configuration for {industry} against OOTB principles: {config_data}. Flag high-customization risks.").text
    st.warning(res)

# --- SECTION 5: NEW HIRE INDUCTION HUB ---
st.markdown("---")
st.header("👤 NEW HIRE INDUCTION HUB")
h_role = st.selectbox("ONBOARDING ROLE", ["PMO", "Change Manager", "Technical Lead", "Implementation Architect", "Process Architect", "Business Analyst", "Business User"])
if st.button("🏁 GENERATE 30-DAY INDUCTION PLAN", key="onboard_btn"):
    res = model.generate_content(f"30-day induction plan for a {h_role} joining a {e_mod} project in the {industry} sector. Include specific industry learning targets.").text
    st.markdown(res)