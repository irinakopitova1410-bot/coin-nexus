import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import base64

# --- CONFIGURAZIONE INTERFACCIA ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e2e8f0; }
    .stMetric { background: rgba(16, 24, 39, 0.8); border: 1px solid #3b82f6; border-radius: 12px; padding: 20px; }
    .stButton>button { background: linear-gradient(90deg, #3b82f6, #2563eb); color: white; border-radius: 8px; font-weight: bold; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTORE GENERAZIONE PDF ---
def create_pdf(totale, mat, rischio, num_voci):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(200, 20, "COIN-NEXUS PLATINUM: AUDIT REPORT", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "1. SINTESI ESECUTIVA", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, f"- Capitale Analizzato: Euro {totale:,.2f}", ln=True)
    pdf.cell(200, 10, f"- Soglia di Materialita (ISA 320): Euro {mat:,.2f}", ln=True)
    pdf.cell(200, 10, f"- Numero di transazioni verificate: {num_voci}", ln=True)
    
    pdf.ln(10)
    pdf
