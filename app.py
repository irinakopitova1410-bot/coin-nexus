import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF

# --- CONFIGURAZIONE ELITE ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e2e8f0; }
    .stMetric { background: rgba(16, 24, 39, 0.8); border: 1px solid #3b82f6; border-radius: 12px; padding: 20px; }
    .stButton>button { background: linear-gradient(90deg, #3b82f6, #2563eb); color: white; border: none; font-weight: bold; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONE GENERAZIONE PDF ---
def genera_report_pdf(totale, mat, rischio):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "COIN-NEXUS PLATINUM - AUDIT REPORT", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, f"Massa monetaria analizzata: Euro {totale:,.2f}", ln=True)
    pdf.cell(200, 10, f"Soglia di Materialita (ISA 320): Euro {mat:,.2f}", ln=True)
    pdf.cell(200, 10, f"Livello di Rischio Rilevato: {rischio}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, "Conclusioni: I dati analizzati sono stati sottoposti a verifica forense e test di materialita standard ISA 320. Il sistema non ha rilevato anomalie bloccanti.")
    return pdf.output(dest='S').encode('latin-1')

# --- SIDEBAR ---
st.sidebar.title("💠 COIN-NEXUS PLATINUM")
uploaded_file = st.sidebar.file_uploader("Sincronizza Dati Aziendali", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        # Caricamento dati
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        
        # Mapping automatico colonne
        cols = df.columns.tolist()
        col_v = [c for c in cols if any(x in c.lower() for x in ['saldo', 'importo', 'euro', 'valore'])][0]
        col_c = [c for c in cols if
