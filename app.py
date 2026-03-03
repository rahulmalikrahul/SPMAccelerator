import streamlit as st
import pandas as pd
import google.generativeai as genai
from fpdf import FPDF
import io
import xlsxwriter
from datetime import datetime

# --- 1. PAGE & UI THEME CONFIGURATION ---
st.set_page_config(page_title="AI Powered ServiceNow Transformation", page_icon="🌐", layout="wide")

# AccelQ-Inspired "Dark Tech" CSS
st.markdown("""
    <style>
    /* Global Background & Base Text */
    .stApp {
        background: radial-gradient(circle at top right, #001a3d, #00041c);
        color: #ffffff;
        font-family: 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Demo Watermark (Background Layer) */
    .watermark {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) rotate(-45deg);
        font-size: 10rem;
        color: rgba(0, 245, 255, 0.04);
        font-weight: 800;
        z-index: 0;
        pointer-events: none;
        white-space: nowrap;
    }

    /* Primary Heading: Large, Bold, Uppercase */
    .main-title {
        color: #00f5ff !important;
        font-size: 2.8rem !important;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-bottom: 5px;
        line-height: 1.2;
    }

    /* Sub-Headings: Mixed Case & Smaller */
    h2, h3, .section-header {
        color: #00f5ff !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        text-transform: none !important; /* Mixed Case */
        margin-top: 25px;
        letter-spacing: 0.5px;
    }
    
    /* Tabs Optimization: Stretch to fill horizontal space */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        width: 100%;
    }
    .stTabs [data-baseweb="tab"] {
        flex: 1; 
        background-color: #001233 !important;
        border: 1px solid #00f5ff33 !important;
        color: #ffffff !important;
        height: 60px;
        font-weight: 600;
        font-size: 1.1rem;
        border-radius: 4px 4px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00f5ff !important;
        color: #00041c !important;
        border: 1px solid #00f5ff !important;
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: #000b2e !important;
        border-right: 1px solid #00f5ff;
    }

    /* Standard Button: Glowing Cyan */
    .stButton>button {
        background-color: #00f5ff !important;
        color: #00041c !important;
        border-radius: 4px !important;
        border: none !important;
        font-weight: 700 !important;
        width: 100%;
        transition: 0.3s all ease;
    }
    .stButton>button:hover {
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.6);
        transform: translateY(-2px);
    }
    </style>
    
    <div class="watermark">DEMO</div>
    """, unsafe_allow_html=True)

# --- 2. LOGO & HEADER SECTION ---
header_col1, header_col2 = st.columns([1, 5])
with header_col1:
    # Infosys Logo
    st.image("https://www.infosys.com/content/dam/infosys-web/en/global-resource/media-resources/infosys-logo-jpeg.jpg", width=140)
with header_col2:
    st.markdown('<h1 class="main-title">AI Powered ServiceNow Transformation</h1>', unsafe_allow_html=True)
    st.caption("Next-Gen Strategic Orchestrator for Enterprise Excellence")

# --- 3. HELPER FUNCTIONS (BINARY SAFE) ---
def get_pdf_bytes(content, title):
    # Fix for Latin-1 encoding issues often found in AI responses
    safe_text = content.encode('latin-1', 'replace').decode('latin-1').replace('?', "'")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(0, 4, 28)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_font("Helvetica", 'B', 18); pdf.set_text_color(0, 245, 255)
    pdf.cell(0, 20, title, ln=True, align='C')
    pdf.set_y(50); pdf.set_text_color(0, 0, 0); pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 7, safe_text)
    # Cast bytearray to bytes to resolve StreamlitAPIException
    return bytes(pdf.output())

def get_excel_bytes(content, sheet_name="Technical Mapping"):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    wrap_format = workbook.add_format({'text_wrap': True, 'valign': 'top'})
    worksheet.write('A1', f'AI Generated {sheet_name}', workbook.add_format({'bold': True, 'font_color': '#00509d'}))
    worksheet.write('A2', content, wrap_format)
    worksheet.set_column('A:A', 100)
    workbook.close()
    return output.getvalue()

# --- 4. API & AI INITIALIZATION ---
secret_key = st.secrets.get("GEMINI_API_KEY")
if secret_key:
    genai.configure(api_key=secret_key)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        ai_ready = True
    except: ai_ready = False
else:
    st.sidebar.error("🔑 API Key Missing")
    ai_ready = False

# --- 5. SESSION STATE ---
modules = ["SPM", "CSDM", "CMDB", "SAMPro", "ITSM"]
if "history" not in st.session_state:
    st.session_state.history = {m: [] for m in modules}
if "tech_map_result" not in st.session_state:
    st.session_state.tech_map_result = ""

# --- 6. SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("### 🛡️ Strategic Control")
    industry = st.selectbox("Industry Focus", 
                          ["Oil & Gas / OT-IT Convergence", "Mining", "Oil Field Services", "Utilities", "Manufacturing", "Healthcare"])
    maturity = st.select_slider("Maturity Level", ["Legacy", "Crawl", "Walk", "Run", "Fly"])
    st.divider()
    st.info(f"Targeting: {industry}\nStrategy: {maturity} Phase")

# --- 7. MODULE AGENT TABS (FULL REAL ESTATE) ---
tabs = st.tabs([f"💠 {m}" for m in modules])

for i, m_name in enumerate(modules):
    with tabs[i]:
        col_chat, col_tools = st.columns([2, 1])
        
        with col_chat:
            st.markdown(f"### {m_name} Cognitive Specialist")
            for msg in st.session_state.history[m_name]:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
            if user_input := st.chat_input(f"Consult {m_name} for {industry}...", key=f"chat_input_{m_name}"):
                st.session_state.history[m_name].append({"role": "user", "content": user_input})
                with st.chat_message("user"): st.markdown(user_input)
                
                if ai_ready:
                    ai_prompt = f"Expert: {m_name} | Industry: {industry} | Maturity: {maturity}. Context: Implementation Best Practices. Query: {user_input}"
                    response = model.generate_content(ai_prompt).text
                    st.session_state.history[m_name].append({"role": "assistant", "content": response})
                    with st.chat_message("assistant"): st.markdown(response)

        with col_tools:
            st.markdown("### Risk Audit")
            if st.button(f"Scan {m_name} Hazards", key=f"risk_{m_name}"):
                with st.spinner("Analyzing Risks..."):
                    risk_res = model.generate_content(f"Identify 3 major risks for {m_name} implementation in {industry}.").text
                    st.error(risk_res)
            
            st.divider()
            st.markdown("### Artifact Generation")
            if st.button(f"Draft {m_name} Roadmap", key=f"btn_plan_{m_name}"):
                with st.spinner("Building Roadmap..."):
                    roadmap = model.generate_content(f"Create a 4-phase transformation roadmap for {m_name} in {industry}.").text
                    st.session_state[f"roadmap_{m_name}"] = roadmap
                    st.success("Roadmap Ready")
            
            if f"roadmap_{m_name}" in st.session_state:
                st.download_button("📥 Roadmap (PDF)", 
                                   data=get_pdf_bytes(st.session_state[f"roadmap_{m_name}"], f"{m_name} Roadmap"),
                                   file_name=f"{m_name}_Roadmap.pdf", key=f"dl_pdf_{m_name}")

# --- 8. ROLE-BASED EXECUTION ENGINE ---
st.divider()
st.header("Role-Based Execution Engine")
r1, r2, r3 = st.columns(3)
with r1: e_role = st.selectbox("Your Professional Role", ["Implementation Architect", "Process Architect", "Technical Lead", "PMO Lead", "Change Management Lead", "Business Analyst"])
with r2: e_stage = st.selectbox("Project Phase", ["Design (Requirements)", "Build (Config)", "Deploy (Validation)"])
with r3: e_mod = st.selectbox("Focus Module", modules, key="exec_ctx")

if st.button("🚀 Generate Phase Action Plan", key="exec_btn"):
    with st.spinner("Calculating Actions..."):
        res = model.generate_content(f"Action plan for a {e_role} during the {e_stage} phase of {e_mod} in {industry}.").text
        st.info(res)

# --- 9. TECHNICAL MAPPING GENERATOR (EXCEL/PDF) ---
st.divider()
st.header("Technical Mapping Generator")
mapping_input = st.text_area("Requirements (e.g. Map Offshore Rig OT sensors to ServiceNow Technical Services):", height=100)
if st.button("📝 Generate Technical Mapping", key="map_btn"):
    with st.spinner("Mapping Data Structures..."):
        st.session_state.tech_map_result = model.generate_content(f"Provide a technical mapping sheet for: {mapping_input} in {e_mod} for {industry}.").text
        st.code(st.session_state.tech_map_result, language="markdown")

if st.session_state.tech_map_result:
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.download_button("📥 Mapping (PDF)", 
                           data=get_pdf_bytes(st.session_state.tech_map_result, "Technical Mapping"), 
                           file_name="Technical_Mapping.pdf")
    with d_col2:
        st.download_button("📥 Mapping (Excel)", 
                           data=get_excel_bytes(st.session_state.tech_map_result), 
                           file_name="Technical_Mapping.xlsx")

# --- 10. OOTB BEST PRACTICE REVIEW ---
st.divider()
st.header("OOTB Best Practice Review")
c_input = st.text_area("Paste Configuration Plan or Customization Proposal:", height=100, key="ootb_area")
if st.button("🔍 Run OOTB Compliance Audit", key="ootb_btn"):
    with st.spinner("Reviewing against OOTB standards..."):
        res = model.generate_content(f"Audit this {e_mod} proposal for {industry} against OOTB best practices: {c_input}").text
        st.warning(res)

# --- 11. NEW HIRE INDUCTION HUB ---
st.divider()
st.header("New Hire Induction Hub")
h_role = st.selectbox("Onboarding Profile", 
                    ["PMO", "Change Manager", "Technical Lead", "Implementation Architect", "Process Architect", "Business Analyst", "Business User"])
if st.button("🏁 Launch 30-Day Induction Plan", key="onboard_btn"):
    with st.spinner("Onboarding..."):
        res = model.generate_content(f"Create a 30-day induction plan for a {h_role} joining a {e_mod} project in the {industry} sector.").text
        st.markdown(res)