import streamlit as st
import pandas as pd
import google.generativeai as genai
from fpdf import FPDF
import os
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="SPM Strategic Pilot", page_icon="🧭", layout="wide")

# --- 🔐 API & MODEL SETUP ---
secret_key = st.secrets.get("GEMINI_API_KEY")
if secret_key:
    genai.configure(api_key=secret_key)
    # Using a 2026 stable-alias to avoid 404s
    model = genai.GenerativeModel('gemini-flash-latest')
    ai_ready = True
else:
    st.error("Missing API Key in Secrets!")
    ai_ready = False

# --- 🧠 SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "roadmap_data" not in st.session_state:
    st.session_state.roadmap_data = ""

# --- 📄 PDF GENERATOR FUNCTION ---
def generate_roadmap_pdf(content, title="SPM Implementation Roadmap"):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_fill_color(0, 71, 171) # ServiceNow Blue
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_font("Arial", 'B', 24)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 20, title, ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d')}", ln=True, align='C')
    
    # Body
    pdf.set_y(50)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, content)
    
    return pdf.output()

# --- 🚀 UI LAYOUT ---
st.title("🧭 SPM Strategic Command Center")

# Sidebar: Executive Dashboard
with st.sidebar:
    st.header("🏢 Client Profile")
    industry = st.selectbox("Industry", ["Financial Services", "Healthcare", "Tech", "Manufacturing"])
    maturity = st.select_slider("Current Maturity", options=["Legacy/Manual", "Crawl", "Walk", "Run"])
    
    st.divider()
    st.header("🛠️ Artifacts")
    if st.button("✨ Generate Executive Roadmap"):
        with st.spinner("Drafting Strategic Plan..."):
            context = f"Industry: {industry}, Maturity: {maturity}. Provide a 4-phase roadmap (Foundation, Crawl, Walk, Run) for ServiceNow SPM."
            response = model.generate_content(context)
            st.session_state.roadmap_data = response.text
            st.success("Roadmap Ready!")

    if st.session_state.roadmap_data:
        pdf_bytes = generate_roadmap_pdf(st.session_state.roadmap_data)
        st.download_button(
            label="📥 Download One-Pager (PDF)",
            data=pdf_bytes,
            file_name="SPM_Executive_Roadmap.pdf",
            mime="application/pdf"
        )

# Main Chat Interface
st.subheader("💬 Strategic Implementation Chat")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Explain the CSDM implications for our Project Portfolio..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if ai_ready:
        with st.chat_message("assistant"):
            chat_context = f"Client: {industry}. Maturity: {maturity}. History: {st.session_state.messages[-3:]}"
            response = model.generate_content(f"{chat_context}\n\nUser Question: {prompt}")
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})