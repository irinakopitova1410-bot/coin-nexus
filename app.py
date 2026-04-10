import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e2e8f0; }
    .stMetric { background: rgba(16, 24, 39, 0.8); border: 1px solid #3b82f6; border-radius: 12px; padding: 20px; }
    .stButton>button { background: linear-gradient(90deg, #3b82f6, #2563eb); color: white; border-radius: 8px; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONE PDF ---
def genera_report_pdf(totale, mat, rischio):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "COIN-NEXUS PLATINUM - AUDIT CERTIFICATION", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, f"Massa monetaria analizzata: Euro {totale:,.2f}", ln=True)
    pdf.cell(200, 10, f"Soglia di Materialita (ISA 320): Euro {mat:,.2f}", ln=True)
    pdf.cell(200, 10, f"Livello di Rischio: {rischio}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, "Conclusioni: L'analisi ha verificato la conformita statistica dei flussi e la presenza di anomalie sopra soglia. Documento valido ai fini della revisione preliminare.")
    return
