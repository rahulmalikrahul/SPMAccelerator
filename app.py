import streamlit as st
import pandas as pd
import google.generativeai as genai
from fpdf import FPDF
import io
import xlsxwriter
from datetime import datetime

# --- 1. THEME & UI ORCHESTRATION ---
st.set_page_config(page_title="AI Powered ServiceNow Transformation", page_icon="🌐", layout="wide")

# Custom CSS for AccelQ Dark Tech Style, Watermark, and Real Estate Optimization
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
        font-size: 10rem;
        color: rgba(0, 245, 255, 0.05);
        font-weight: 800;
        z-index: 0;
        pointer-events: none;
        white-space: nowrap;
    }

    /* Primary Heading: Uppercase & Large */
    .main-title {
        color: #00f5ff !important;
        font-size: 2.8rem !important;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* Sub-Headings: Mixed Case & Smaller */
    h2, h3, .section-header {
        color: #00f5ff !important;
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        text-transform: none !important;
        margin-top: 20px;
    }
    
    /* Tabs: Full Width Real Estate */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        width: 100%;
    }
    .stTabs [data-baseweb="tab"] {
        flex: 1; 
        background-color: #001233 !important;
        border: 1px solid #00f5ff33 !important;
        color: #ffffff !important;
        height: 55px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00f5ff !important;
        color: #00041c !important;
    }

    /* Sidebar Styling */
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

# --- 2. BRANDING HEADER ---
logo_col, title_col = st.columns([1, 4])
with logo_col:
    # Infosys Logo
    st.image("https://www.infosys.com/content/dam/infosys-web/en/global-resource/media-resources/infosys-logo-jpeg.jpg", width=130)
with title_col:
    st.markdown('<h1 class="main-title">AI Powered ServiceNow Transformation</h1>', unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS (FIXED FOR BINARY ERRORS) ---
def get_pdf_bytes(content, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(0, 4, 28)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_font("Helvetica", 'B', 18); pdf.set_text_color(0, 245, 255)
    pdf.cell(0, 20, title, ln=True, align='C')
    pdf.set_y(50); pdf.set_text_color(0, 0, 0); pdf.set_font("Helvetica", size=10)
    # Sanitize and write
    safe_text = content.encode('latin-1', 'replace').decode('latin-1').replace('?', "'")
    pdf.multi_cell(0, 7, safe_text)
    # CRITICAL FIX: Cast bytearray to bytes
    return bytes(pdf.output())

def get_excel_bytes(content):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', 'AI Generated Technical Mapping')
    worksheet.write('A2', content)
    workbook.close()
    return output.getvalue()

# --- 4. CORE ENGINE & TABS ---
modules = ["SPM", "CSDM", "CMDB", "SAMPro", "ITSM"]
tabs = st.tabs([f"💠 {m}" for m in modules])

# ... [The rest of your logic follows the same pattern as previous versions]