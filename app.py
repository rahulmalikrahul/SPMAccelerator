import streamlit as st
import pandas as pd
import google.generativeai as genai
from fpdf import FPDF
import io
import xlsxwriter
from datetime import datetime

# --- 1. PREMIUM UI & THEME CONFIGURATION ---
st.set_page_config(page_title="AI Powered ServiceNow Transformation", page_icon="🌐", layout="wide")

# AccelQ-Inspired "Dark Tech" CSS
st.markdown("""
    <style>
    /* Global Background: Deep Navy/Black Gradient */
    .stApp {
        background: radial-gradient(circle at top right, #001a3d, #00041c);
        color: #ffffff;
        font-family: 'Segoe UI', Roboto, sans-serif;
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

    /* Primary Heading: Uppercase & Glowing Cyan */
    .main-title {
        color: #00f5ff !important;
        font-size: 2.8rem !important;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 5px;
    }

    /* Sub-Headings: Mixed Case */
    h2, h3, .section-header {
        color: #00f5ff !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        text-transform: none !important; 
        margin-top: 25px;
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
        border-radius: 4px 4px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00f5ff !important;
        color: #00041c !important;
    }

    /* Standard Button: Glowing Cyan */
    .stButton>button {
        background-color: #00f5ff !important;
        color: #00041c !important;
        border-radius: 4px !important;
        border: none !important;
        font-weight: 700 !important;
        transition: 0.3s all ease;
    }
    .stButton>button:hover {
        box-shadow: 0 0 15px rgba(0, 245, 255, 0.6);
        transform: translateY(-2px);
    }
    </style>
    <div class="watermark">DEMO</div>
    """, unsafe_allow_html=True)

# --- 2. BRANDING & HEADER ---
header_col1, header_col2 = st.columns([1, 5])
with header_col1:
    st.image("https://www.infosys.com/content/dam/infosys-web/en/global-resource/media-resources/infosys-logo-jpeg.jpg", width=140)
with header_col2:
    st.markdown('<h1 class="main-title">AI Powered ServiceNow Transformation</h1>', unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS (FIXED FOR BINARY ERRORS) ---
def sanitize(text):
    return text.encode('latin-1', 'replace').decode('latin-1').replace('?', "'")

def create_pdf(content, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(0, 4, 28)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_font("Helvetica", 'B', 18); pdf.set_text_color(0, 245, 255)
    pdf.cell(0, 20, sanitize(title), ln=True, align='C')
    pdf.set_y(50); pdf.set_text_color(0, 0, 0); pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 7, sanitize(content))
    # FIX: Cast bytearray to bytes to prevent StreamlitAPIException
    return bytes(pdf.output())

def create_excel(content, sheet_name):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', f'Generated {sheet_name}')
    worksheet.write('A2', content)
    workbook.close()
    return output.getvalue()

# --- 4. API & AI INITIALIZATION ---
secret_key = st.secrets.get("GEMINI_API_KEY")
if secret_key:
    genai.configure(api_key=secret_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    ai_ready = True
else:
    st.sidebar.error("🔑 API Key Missing")
    ai_ready = False

# --- 5. SESSION STATE ---
modules = ["SPM", "CSDM", "CMDB", "SAMPro", "ITSM"]
if "history" not in st.session_state:
    st.session_state.history = {m: [] for m in modules}
if "plans" not in st.session_state:
    st.session_state.plans = {m: "" for m in modules}

# --- 6. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🛡️ Strategic Governance")
    industry = st.selectbox("Industry Focus", ["Oil & Gas", "Mining", "Utilities", "Manufacturing"])
    maturity = st.select_slider("Maturity Level", ["Legacy", "Crawl", "Walk", "Run", "Fly"])

# --- 7. MODULE AGENTS (EXPANDED TABS) ---
tabs = st.tabs([f"🔹 {m}" for m in modules])

for i, m_name in enumerate(modules):
    with tabs[i]:
        col_chat, col_tools = st.columns([2, 1])
        
        with col_chat:
            st.subheader(f"{m_name} Cognitive Specialist")
            for msg in st.session_state.history[m_name]:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
            if user_input := st.chat_input(f"Consult {m_name} Expert...", key=f"chat_{m_name}"):
                st.session_state.history[m_name].append({"role": "user", "content": user_input})
                with st.chat_message("user"): st.markdown(user_input)
                
                if ai_ready:
                    prompt = f"Agent: {m_name} Specialist for {industry}. Query: {user_input}"
                    response = model.generate_content(prompt).text
                    st.session_state.history[m_name].append({"role": "assistant", "content": response})
                    with st.chat_message("assistant"): st.markdown(response)

        with col_tools:
            st.subheader("🚩 Project Auditor")
            if st.button(f"Scan {m_name} Risks", key=f"risk_{m_name}"):
                st.error(f"Hazard detected in {m_name} for {industry} industry standards.")
            
            st.divider()
            st.subheader("📋 Implementation Roadmap")
            if st.button(f"Generate 7-Step Plan", key=f"plan_{m_name}"):
                # Based on the Workflow Automation Image
                roadmap = (
                    "How to implement ServiceNow Workflow Automation:\n\n"
                    "Step 1: Define Test Scope & Objectives\n"
                    "Step 2: Choose the Best Tools (e.g., AccelQ)\n"
                    "Step 3: Test Case Design & Script Development\n"
                    "Step 4: Build Test Environment\n"
                    "Step 5: Execute Tests\n"
                    "Step 6: Monitor & Report\n"
                    "Step 7: Improvement & Maintenance"
                )
                st.session_state.plans[m_name] = roadmap
                st.success("7-Step Roadmap Ready")
            
            if st.session_state.plans[m_name]:
                st.download_button("📥 Roadmap (PDF)", 
                                   create_pdf(st.session_state.plans[m_name], f"{m_name} Strategy"), 
                                   f"{m_name}_Roadmap.pdf", key=f"dl_pdf_{m_name}")

# --- 8. TECHNICAL MAPPING GENERATOR ---
st.divider()
st.header("🛠️ Technical Mapping Generator")
mapping_input = st.text_area("Describe Requirements (e.g. Map OT sensors to CSDM Technical Services):")
if st.button("📝 Generate Technical Mapping"):
    map_res = f"Technical Mapping Sheet for {industry}:\nSource Field -> Target Field (CMDB Asset)\nMapping Logic: Industrial IoT Integration."
    st.session_state.mapping_data = map_res
    st.code(map_res)

if "mapping_data" in st.session_state:
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("📥 Mapping (PDF)", create_pdf(st.session_state.mapping_data, "Mapping"), "Mapping.pdf")
    with c2:
        st.download_button("📥 Mapping (Excel)", create_excel(st.session_state.mapping_data, "Mapping"), "Mapping.xlsx")

# --- 9. NEW HIRE INDUCTION HUB ---
st.divider()
st.header("👤 New Hire Induction Hub")
h_role = st.selectbox("Role", ["Technical Lead", "Business Analyst", "PMO Lead", "Implementation Architect"])
if st.button("🏁 Launch 30-Day Induction"):
    st.info(f"Generated a 30-day onboarding plan for a {h_role} in the {industry} sector.")