import streamlit as st
import pandas as pd
import google.generativeai as genai
from fpdf import FPDF
import io
import xlsxwriter
from datetime import datetime

# --- 🎨 ACCELQ-INFOSYS HYBRID UI THEME ---
st.set_page_config(page_title="AI Powered ServiceNow Transformation", page_icon="🌐", layout="wide")

# Custom CSS for the "Demo" Look, Logos, and Real Estate Optimization
st.markdown("""
    <style>
    /* Background & Global Text */
    .stApp {
        background: radial-gradient(circle at top right, #001a3d, #00041c);
        color: #ffffff;
    }
    
    /* Main Title (Stay Large/Uppercase) */
    .main-title {
        color: #00f5ff !important;
        font-size: 2.8rem !important;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-bottom: 0px;
    }

    /* Sub-Headings (Smaller & Mixed Case) */
    h2, h3 {
        color: #00f5ff !important;
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        text-transform: none !important; /* Mixed Case */
        letter-spacing: 1px;
    }
    
    /* Watermark */
    .watermark {
        position: fixed;
        top: 10px;
        right: 20px;
        opacity: 0.3;
        font-size: 3rem;
        color: #ffffff;
        font-weight: bold;
        z-index: 1000;
        pointer-events: none;
    }

    /* Tab Expansion - Cover Real Estate */
    button[data-baseweb="tab"] {
        flex: 1; /* Stretch tabs to fill width */
        min-width: 150px;
        background-color: #001233 !important;
        border: 1px solid #00f5ff33 !important;
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    button[aria-selected="true"] {
        background-color: #00f5ff !important;
        color: #00041c !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #000b2e !important;
        border-right: 1px solid #00f5ff;
    }

    /* Standard Button Styling */
    .stButton>button {
        background-color: #00f5ff !important;
        color: #00041c !important;
        border-radius: 4px;
        font-weight: 700;
        text-transform: none;
    }
    </style>
    
    <div class="watermark">DEMO</div>
    """, unsafe_allow_html=True)

# --- 🏢 LOGO SECTION ---
logo_col, title_col = st.columns([1, 4])
with logo_col:
    # Placeholder for Infosys Logo - Use actual URL if available
    st.image("https://www.infosys.com/content/dam/infosys-web/en/global-resource/media-resources/infosys-logo-jpeg.jpg", width=120)
with title_col:
    st.markdown('<h1 class="main-title">AI Powered ServiceNow Transformation</h1>', unsafe_allow_html=True)

# --- 🔐 API & MODEL SETUP ---
secret_key = st.secrets.get("GEMINI_API_KEY")
if secret_key:
    genai.configure(api_key=secret_key)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        ai_ready = True
    except: ai_ready = False
else:
    ai_ready = False

# --- 🧠 STATE MANAGEMENT ---
modules = ["SPM", "CSDM", "CMDB", "SAMPro", "ITSM"]
if "history" not in st.session_state:
    st.session_state.history = {m: [] for m in modules}
if "plans" not in st.session_state:
    st.session_state.plans = {m: "" for m in modules}
if "tech_map" not in st.session_state:
    st.session_state.tech_map = ""

# --- 📄 EXPORT UTILITIES (FIXED BINARY DATA) ---
def create_pdf_bytes(content, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(0, 4, 28)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_font("Helvetica", 'B', 18); pdf.set_text_color(0, 245, 255)
    pdf.cell(0, 20, title.encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')
    pdf.set_y(50); pdf.set_text_color(0, 0, 0); pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 7, content.encode('latin-1', 'replace').decode('latin-1'))
    # IMPORTANT: Convert bytearray to bytes to fix Streamlit binary error
    return bytes(pdf.output())

def create_excel_bytes(content, sheet_name):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', f'{sheet_name} Content')
    worksheet.write('A2', content)
    workbook.close()
    return output.getvalue()

# --- 🏗️ SIDEBAR ---
with st.sidebar:
    st.markdown("### Core Control")
    industry = st.selectbox("Industry Focus", ["Oil & Gas", "Mining", "Oil Field Services", "Utilities", "Manufacturing"])
    maturity = st.select_slider("Maturity Level", ["Legacy", "Crawl", "Walk", "Run", "Fly"])
    st.divider()
    st.caption("AI Orchestrator v2.6.3")

# --- SECTION 1: TRANSFORMATION AGENTS (Expanded Tabs) ---
tabs = st.tabs([f"💠 {m}" for m in modules])

for i, m_name in enumerate(modules):
    with tabs[i]:
        col_chat, col_tools = st.columns([2, 1])
        with col_chat:
            st.markdown(f"### {m_name} Cognitive Agent")
            for msg in st.session_state.history[m_name]:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
            if user_input := st.chat_input(f"Message {m_name} Agent...", key=f"chat_{m_name}"):
                st.session_state.history[m_name].append({"role": "user", "content": user_input})
                with st.chat_message("user"): st.markdown(user_input)
                
                if ai_ready:
                    response = model.generate_content(f"Module: {m_name}, Industry: {industry}. {user_input}").text
                    st.session_state.history[m_name].append({"role": "assistant", "content": response})
                    with st.chat_message("assistant"): st.markdown(response)

        with col_tools:
            st.markdown("### Risk Auditor")
            if st.button(f"Scan {m_name} Risks", key=f"audit_{m_name}"):
                st.error("Audit Report: Industry-specific customization risks detected in Demand management.")
            
            st.divider()
            if st.button(f"Generate {m_name} Roadmap", key=f"plan_{m_name}"):
                st.session_state.plans[m_name] = f"Detailed 4-Phase Implementation Strategy for {m_name} in {industry}..."
                st.success("Plan Generated")
            
            if st.session_state.plans[m_name]:
                st.download_button("📥 Download One-Pager (PDF)", 
                                   data=create_pdf_bytes(st.session_state.plans[m_name], f"{m_name} Roadmap"), 
                                   file_name=f"{m_name}_Plan.pdf")

# --- SECTION 2: ROLE-BASED EXECUTION ENGINE ---
st.divider()
st.header("Role-Based Execution Engine")
r_col, s_col, m_col = st.columns(3)
with r_col: role = st.selectbox("Your Role", ["Implementation Architect", "Technical Lead", "PMO Lead", "Business Analyst"])
with s_col: stage = st.selectbox("Current Phase", ["Design", "Build", "Deploy"])
with m_col: mod_ctx = st.selectbox("Focus Module", modules, key="exec_mod")

if st.button("🚀 Generate Action Plan", key="exec_btn"):
    st.info(f"Generated specific guidance for the {role} during the {stage} phase of {mod_ctx}.")

# --- SECTION 3: TECHNICAL MAPPING & OOTB REVIEW ---
st.divider()
st.header("Technical Mapping & OOTB Review")
c1, c2 = st.columns([2,1])
with c1:
    mapping_desc = st.text_area("Describe Technical Requirements (e.g. Asset CI Mapping):", height=100)
    if st.button("📝 Generate Technical Mapping", key="map_btn"):
        st.session_state.tech_map = "Table: cmdb_ci_hardware -> Field: u_asset_tag..."
        st.code(st.session_state.tech_map)
        
    if st.session_state.tech_map:
        d1, d2 = st.columns(2)
        with d1:
            st.download_button("📥 PDF Mapping", create_pdf_bytes(st.session_state.tech_map, "Technical Mapping"), "Mapping.pdf")
        with d2:
            st.download_button("📥 Excel Mapping", create_excel_bytes(st.session_state.tech_map, "Mapping"), "Mapping.xlsx")
with c2:
    st.subheader("OOTB Audit")
    if st.button("🔍 Run Best Practice Review"):
        st.warning("Audit Result: Recommended using standard CSDM Service relations instead of custom reference fields.")

# --- SECTION 4: INDUCTION HUB ---
st.divider()
st.header("New Hire Induction Hub")
h_role = st.selectbox("Onboarding Position", ["Technical Lead", "Business Analyst", "Business User"], key="onboard_role")
if st.button("🏁 Start 30-Day Plan"):
    st.markdown(f"### Induction Plan: {h_role}\n* Week 1: Platform Orientation\n* Week 2: Industry Context ({industry})\n* Week 3: Project Deep Dive...")