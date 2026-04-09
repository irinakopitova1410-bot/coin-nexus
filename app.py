import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF

# --- CONFIGURAZIONE INTERFACCIA ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM", layout="wide")

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

# --- FUNZIONE GENERAZIONE PDF ---
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
    pdf.cell(200, 8, f"- Soglia Materialita (ISA 320): Euro {mat:,.2f}", ln=True)
    pdf.cell(200, 8, f"- Numero Record Verificati: {num_voci}", ln=True)
    pdf.cell(200, 8, f"- Livello di Rischio: {rischio}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 8, "Il presente report attesta la verifica di integrita statistica e conformita ISA 320.")
    return pdf.output()

# --- SIDEBAR ---
st.sidebar.title("💠 COIN-NEXUS PLATINUM")
uploaded_file = st.sidebar.file_uploader("Carica Dataset", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        
        # Mapping Automatico Colonne
        cols = df.columns.tolist()
        col_v = [c for c in cols if any(x in c.lower() for x in ['saldo', 'importo', 'euro', 'valore'])][0]
        col_c = [c for c in cols if any(x in c.lower() for x in ['desc', 'voce', 'conto', 'account'])][0]
        df[col_v] = pd.to_numeric(df[col_v].astype(str).replace('[€, ]', '', regex=True), errors='coerce').fillna(0)

        st.title("🛡️ Audit Intelligence & Forensic")

        # Metriche
        totale = df[col_v].sum()
        mat = totale * 0.01
        rischio = "BASSO" if totale < 1000000 else "MODERATO"

        m1, m2, m3 = st.columns(3)
        m1.metric("CAPITALE ANALIZZATO", f"
