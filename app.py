import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF

# --- CONFIGURAZIONE ELITE ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM", layout="wide")

# CSS per interfaccia Premium
st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e2e8f0; }
    .stMetric { background: rgba(16, 24, 39, 0.8); border: 1px solid #3b82f6; border-radius: 12px; padding: 20px; }
    .stButton>button { 
        background: linear-gradient(90deg, #3b82f6, #2563eb); 
        color: white; border: none; font-weight: bold; border-radius: 8px; width: 100%; height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MOTORE GENERAZIONE PDF ---
def genera_report_pdf(totale, mat, rischio, num_voci):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "COIN-NEXUS PLATINUM - AUDIT CERTIFICATION", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "SINTESI ANALISI FINANZIARIA", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(200, 8, f"- Massa Monetaria Totale: Euro {totale:,.2f}", ln=True)
    pdf.cell(200, 8, f"- Soglia Materialita (ISA 320): Euro {mat:
