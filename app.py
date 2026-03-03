import streamlit as st
import pandas as pd
import google.generativeai as genai
from fpdf import FPDF
import io
import xlsxwriter
from datetime import datetime

# --- 🎨 ACCELQ DARK TECH THEME ---
st.set_page_config(page_title="AI Powered ServiceNow Transformation", page_icon="🌐", layout="wide")

# Custom CSS for UI Real Estate, Watermark, and Branding
st.markdown("""
    <style>
    /* Background & Global Font */
    .stApp {
        background: radial-gradient(circle at top right, #001a3d, #00041c);
        color: #ffffff;
    }
    
    /* Demo Watermark */
    .watermark {
        position: fixed;
        top: 10px;
        right: 20px;
        opacity: 0.2;
        font-size: 3.5rem;
        color: #ffffff;
        font-weight: 800;
        z-index: 1000;
        pointer-events: none;
        letter-spacing: 5px;
    }

    /* Main Title (Maintained as Uppercase/Large) */
    .main-title {
        color: #00f5ff !important;
        font-size: 2.8rem !important;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0px;
    }

    /* Sub-Headings (Mixed Case & Smaller) */
    h2, h3, .section-header {
        color: #00f5ff !important;
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        text-transform: none !important; /* Mixed Case */
        margin-top: 20px;
    }
    
    /* Tab Expansion - Cover Real Estate */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        width: 100%;
    }
    .stTabs [data-baseweb="tab"] {
        flex: 1; /* Stretch tabs across the width */
        background-color: #001233 !important;
        border: 1px solid #00f5ff33 !important;
        color: #ffffff !important;
        height: 55px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00f5ff !important;
        color: #00041c !important;
        border: 1px solid #00f5ff !important;
    }

    /* Sidebar Accents */
    section[data-testid="stSidebar"] {
        background-color: #000b2e !important;
        border-right: 1px solid #00f5ff;
    }

    /* Glowing Buttons */
    .stButton>button {
        background-color: #00f5ff !important;
        color: #00041c !important;
        border-radius: 4px;
        font-weight: 700;
        border: none;
    }
    </style>
    
    <div class="watermark">DEMO</div>
    """, unsafe_allow_html=True)

# --- 🏢 LOGO & HEADER ---
logo_col, title_col = st.columns([1, 4])
with logo_col:
    # Official Infosys Logo
    st.image("https://www.infosys.com/content/dam/infosys-web/en/global-resource/media-resources/infosys-logo-jpeg.jpg", width=140)
with title_col:
    st.markdown('<h1 class="main-title">AI Powered ServiceNow Transformation</h1>', unsafe_allow_html=True)

# --- 🔐 API SETUP ---
secret_key = st.secrets.get("GEMINI_API_KEY")
if secret_key:
    genai.configure(api_key=secret_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    ai_ready = True
else:
    st.sidebar.warning("API Key missing in secrets.")
    ai_ready = False

# --- 🛠️ HELPER FUNCTIONS (BINARY FIX) ---
def create_pdf_bytes(content, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(0, 4, 28)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_font("Helvetica", 'B', 18); pdf.set_text_color(0, 245, 255)
    pdf.cell(0, 20, title, ln=True, align='C')
    pdf.set_y(50); pdf.set_text_color(0, 0, 0); pdf.set_font("Helvetica", size=10)
    # Sanitize content for PDF
    safe_text = content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, safe_text)
    # FIX: Explicitly cast bytearray to bytes
    return bytes(pdf.output())

def create_excel_bytes(content):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', 'AI Generated Insight')
    worksheet.write('A2', content)
    workbook.close()
    return output.getvalue()

# --- 🧠 SESSION STATE ---
modules = ["SPM", "CSDM", "CMDB", "SAMPro", "ITSM"]
if "history" not in st.session_state:
    st.session_state.history = {m: [] for m in modules}

# --- 🏗️ SIDEBAR ---
with st.sidebar:
    st.markdown("### Strategic Filters")
    industry = st.selectbox("Industry", ["Oil & Gas", "Utilities", "Mining", "Manufacturing"])
    maturity = st.select_slider("Phase", ["Legacy", "Crawl", "Walk", "Run", "Fly"])

# --- 💠 MODULE WORKSTREAMS ---
tabs = st.tabs([f"🔹 {m}" for m in modules])

for i, m_name in enumerate(modules):
    with tabs[i]:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown(f"### {m_name} Cognitive Agent")
            for msg in st.session_state.history[m_name]:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
            if user_input := st.chat_input(f"Consult {m_name}...", key=f"chat_{m_name}"):
                st.session_state.history[m_name].append({"role": "user", "content": user_input})
                with st.chat_message("user"): st.markdown(user_input)
                if ai_ready:
                    res = model.generate_content(f"You are a {m_name} expert for {industry}. User asks: {user_input}").text
                    st.session_state.history[m_name].append({"role": "assistant", "content": res})
                    st.rerun()

        with c2:
            st.markdown("### Management Tools")
            if st.button(f"Draft {m_name} Roadmap", key=f"btn_{m_name}"):
                plan = f"Roadmap for {m_name} in {industry}:\n1. Assessment\n2. Alignment\n3. Execution\n4. Optimization"
                st.session_state[f"temp_plan_{m_name}"] = plan
                st.success("Roadmap Generated")
            
            if f"temp_plan_{m_name}" in st.session_state:
                st.download_button("📥 Download PDF", 
                                   create_pdf_bytes(st.session_state[f"temp_plan_{m_name}"], f"{m_name} Roadmap"), 
                                   f"{m_name}_Plan.pdf")

# --- ⚙️ EXECUTION & MAPPING ---
st.divider()
st.header("Strategic Execution Engine")
r1, r2, r3 = st.columns(3)
with r1: role = st.selectbox("Role", ["Architect", "Process Lead", "Technical Lead", "Business Analyst", "PMO"])
with r2: phase = st.selectbox("Current Phase", ["Design", "Build", "Deploy"])
with r3: mod_exec = st.selectbox("Module Focus", modules, key="exec_mod")

if st.button("🚀 Generate Action Plan"):
    res = model.generate_content(f"Create action plan for {role} during {phase} of {mod_exec} in {industry}.").text
    st.info(res)

st.divider()
st.header("Technical Mapping Generator")
mapping_input = st.text_area("Requirements for Mapping:")
if st.button("Generate Mapping"):
    map_res = f"Technical Mapping Logic for {mod_exec}:\nSource: {mapping_input}\nTarget: cmdb_ci_hardware"
    st.code(map_res)
    st.download_button("📥 Download Excel", create_excel_bytes(map_res), "Mapping.xlsx")