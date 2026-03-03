import streamlit as st
import pandas as pd
import google.generativeai as genai
from fpdf import FPDF
import io
import xlsxwriter

# --- 🎨 THEME & UI ORCHESTRATION ---
st.set_page_config(page_title="AI Powered ServiceNow Transformation", page_icon="🌐", layout="wide")

# Custom CSS for the "Wow" Factor: AccelQ-inspired Colors & Layout
st.markdown("""
    <style>
    /* Main Background & Fonts */
    .stApp {
        background: radial-gradient(circle at top right, #001a3d, #00041c);
        color: #ffffff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Watermark */
    .watermark {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) rotate(-45deg);
        font-size: 10rem;
        color: rgba(255, 255, 255, 0.05);
        font-weight: bold;
        z-index: 1000;
        pointer-events: none;
        white-space: nowrap;
    }

    /* Main Title: Large & Uppercase */
    .main-title {
        color: #00f5ff !important;
        font-size: 2.5rem !important;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: -20px;
    }

    /* Sub-Headings: Mixed Case & Smaller */
    h2, h3 {
        color: #00f5ff !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        text-transform: none !important; /* Mixed Case */
        margin-top: 20px;
    }
    
    /* Tabs: Stretch to cover real estate */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        width: 100%;
    }
    .stTabs [data-baseweb="tab"] {
        flex: 1; /* Cover real estate */
        background-color: #001233 !important;
        border: 1px solid #00f5ff33 !important;
        color: #ffffff !important;
        height: 60px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00f5ff !important;
        color: #00041c !important;
        border: 1px solid #00f5ff !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #000b2e !important;
        border-right: 1px solid #00f5ff;
    }

    /* Button Styling - Glowing Cyan */
    .stButton>button {
        background-color: #00f5ff !important;
        color: #00041c !important;
        border-radius: 4px;
        font-weight: 700;
        border: none;
        width: 100%;
    }
    .stButton>button:hover {
        box-shadow: 0 0 15px #00f5ff;
    }
    </style>
    
    <div class="watermark">DEMO</div>
    """, unsafe_allow_html=True)

# --- 🏢 LOGO & HEADER ---
logo_col, title_col = st.columns([1, 5])
with logo_col:
    # Standard Infosys Logo URL
    st.image("https://www.infosys.com/content/dam/infosys-web/en/global-resource/media-resources/infosys-logo-jpeg.jpg", width=120)
with title_col:
    st.markdown('<h1 class="main-title">AI Powered ServiceNow Transformation</h1>', unsafe_allow_html=True)

# --- 🔐 API SETUP ---
secret_key = st.secrets.get("GEMINI_API_KEY")
if secret_key:
    genai.configure(api_key=secret_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    ai_ready = True
else:
    ai_ready = False

# --- 🧠 STATE MANAGEMENT ---
modules = ["SPM", "CSDM", "CMDB", "SAMPro", "ITSM"]
if "history" not in st.session_state:
    st.session_state.history = {m: [] for m in modules}
if "tech_map" not in st.session_state:
    st.session_state.tech_map = ""

# --- 📄 EXPORT HELPERS (FIXED BINARY DATA) ---
def get_pdf_bytes(content, title):
    # Sanitize for Latin-1
    safe_content = content.encode('latin-1', 'replace').decode('latin-1').replace('?', "'")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(0, 4, 28)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_font("Helvetica", 'B', 18); pdf.set_text_color(0, 245, 255)
    pdf.cell(0, 20, title, ln=True, align='C')
    pdf.set_y(50); pdf.set_text_color(0, 0, 0); pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 7, safe_content)
    # FIX: Explicitly cast bytearray to bytes
    return bytes(pdf.output())

def