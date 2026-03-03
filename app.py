import streamlit as st
import pandas as pd
import google.generativeai as genai
from fpdf import FPDF
import io
import xlsxwriter

# --- 1. PAGE & UI CONFIGURATION ---
st.set_page_config(page_title="AI Powered ServiceNow Transformation", page_icon="🌐", layout="wide")

# AccelQ-Inspired CSS: Deep Navy Gradient, Glowing Cyan, Mixed Case Headings
st.markdown("""
    <style>
    /* Global Background */
    .stApp {
        background: radial-gradient(circle at top right, #001a3d, #00041c);
        color: #ffffff;
    }
    
    /* Demo Watermark */
    .watermark {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) rotate(-45deg);
        font-size: 8rem;
        color: rgba(0, 245, 255, 0.05);
        font-weight: bold;
        z-index: 0;
        pointer-events: none;
        white-space: nowrap;
    }

    /* Titles & Headings */
    .main-title {
        color: #00f5ff !important;
        font-size: 2.6rem !important;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 10px;
    }
    
    /* Mixed Case Subheadings */
    h2, h3, .section-header {
        color: #00f5ff !important;
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        text-transform: none !important;
        margin-top: 15px;
    }

    /* Tabs: Full Width Real Estate */
    .stTabs [data-baseweb="tab-list"] {
        gap: 5px;
        width: 100%;
    }
    .stTabs [data-baseweb="tab"] {
        flex: 1; 
        background-color: #001233 !important;
        border: 1px solid #00f5ff33 !important;
        color: #ffffff !important;
        height: 50px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00f5ff !important;
        color: #00041c !important;
    }

    /* Sidebar and Buttons */
    section[data-testid="stSidebar"] {
        background-color: #000b2e !important;
        border-right: 1px solid #00f5ff;
    }
    .stButton>button {
        background-color: #00f5ff !important;
        color: #00041c !important;
        font-weight: 700;
        border-radius: 4px;
        width: 100%;
    }
    </style>
    <div class="watermark">DEMO</div>
    """, unsafe_allow_html=True)

# --- 2. BRANDING & HEADER ---
col_logo, col_title = st.columns([1, 5])
with col_logo:
    # Official Infosys Logo
    st.image("https://www.infosys.com/content/dam/infosys-web/en/global-resource/media-resources/infosys-logo-jpeg.jpg", width=120)
with col_title:
    st.markdown('<h1 class="main-title">AI Powered ServiceNow Transformation</h1>', unsafe_allow_html=True)

# --- 3. API INITIALIZATION ---
secret_key = st.secrets.get("GEMINI_API_KEY")
if secret_key:
    genai.configure(api_key=secret_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    ai_ready = True
else:
    st.sidebar.error("🔑 API Key Missing")
    ai_ready = False

# --- 4. STATE & HELPERS ---
modules = ["SPM", "CSDM", "CMDB", "SAMPro", "ITSM"]
if "history" not in st.session_state:
    st.session_state.history = {m: [] for m in modules}
if "tech_map" not in st.session_state:
    st.session_state.tech_map = ""

def get_pdf_bytes(content, title):
    # Encoding fix for AI text and binary conversion
    safe_text = content.encode('latin-1', 'replace').decode('latin-1').replace('?', "'")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(0, 4, 28)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_font("Helvetica", 'B', 16); pdf.set_text_color(0, 245, 255)
    pdf.cell(0, 20, title, ln=True, align='C')
    pdf.set_y(50); pdf.set_text_color(0, 0, 0); pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 7, safe_text)
    # Binary fix: explicitly cast bytearray to bytes
    return bytes(pdf.output())

def get_excel_bytes(content):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', 'AI Generated Technical Mapping')
    worksheet.write('A2', content)
    workbook.close()
    return output.getvalue()

# --- 5. SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("### Strategic Settings")
    industry = st.selectbox("Industry Focus", 
                          ["Oil & Gas / OT-IT Convergence", "Mining", "Oil Field Services", "Utilities", "Manufacturing", "Public Sector"])
    maturity = st.select_slider("Maturity Level", ["Legacy", "Crawl", "Walk", "Run", "Fly"])
    st.divider()
    st.caption("Infosys Digital Transformation Engine")

# --- 6. AGENT WORKSTREAMS (TABS) ---
tabs = st.tabs([f"💠 {m}" for m in modules])

for i, m_name in enumerate(modules):
    with tabs[i]:
        c_chat, c_tools = st.columns([2, 1])
        with c_chat:
            st.markdown(f"### {m_name} Cognitive Consultant")
            for msg in st.session_state.history[m_name]:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
            if prompt := st.chat_input(f"Consult {m_name} for {industry}...", key=f"chat_{m_name}"):
                st.session_state.history[m_name].append({"role": "user", "content": prompt})
                with st.chat_message("user"): st.markdown(prompt)
                
                if ai_ready:
                    ai_prompt = f"Expert: {m_name} | Industry: {industry} | Maturity: {maturity}. Respond to: {prompt}"
                    response = model.generate_content(ai_prompt).text
                    st.session_state.history[m_name].append({"role": "assistant", "content": response})
                    with st.chat_message("assistant"): st.markdown(response)