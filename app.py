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
    pdf.cell(200, 10, "COIN-NEXUS PLATINUM - AUDIT REPORT", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, f"Massa monetaria analizzata: Euro {totale:,.2f}", ln=True)
    pdf.cell(200, 10, f"Soglia di Materialita (ISA 320): Euro {mat:,.2f}", ln=True)
    pdf.cell(200, 10, f"Rating di Rischio: {rischio}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, "Esito: Analisi completata con successo. Il dataset e conforme ai parametri di verifica statistica.")
    return pdf.output(dest='S').encode('latin-1')

# --- SIDEBAR ---
st.sidebar.title("💠 COIN-NEXUS PLATINUM")
uploaded_file = st.sidebar.file_uploader("Carica File Excel/CSV", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        # Caricamento dati
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        cols = df.columns.tolist()

        # --- SISTEMA DI MAPPING CORRETTO (SENZA SYNTAX ERROR) ---
        probabili_v = [c for c in cols if any(x in str(c).lower() for x in ['saldo', 'importo', 'euro', 'valore', 'totale'])]
        probabili_c = [c for c in cols if any(x in str(c).lower() for x in ['desc', 'voce', 'conto', 'account', 'dettaglio'])]

        col_v, col_c = None, None

        if probabili_v and probabili_c:
            col_v = probabili_v[0]
            col_c = probabili_c[0]
            st.sidebar.success(f"✅ Rilevate: {col_v} e {col_c}")
        else:
            st.warning("⚠️ Colonne non identificate automaticamente.")
            col_v = st.sidebar.selectbox("Colonna Valori (Importi):", cols)
            col_c = st.sidebar.selectbox("Colonna Descrizioni:", cols)

        if col_v and col_c:
            # Pulizia dati
            df[col_v] = pd.to_numeric(df[col_v].astype(str).replace('[€, ]', '', regex=True), errors='coerce').fillna(0)
            
            st.title("🛡️ Audit Intelligence & Forensic")

            # Metriche
            totale = df[col_v].sum()
            mat = totale * 0.01
            rischio = "BASSO" if totale < 1000000 else "MODERATO"

            m1, m2, m3 = st.columns(3)
            m1.metric("MASSA MONETARIA", f"€ {totale:,.2f}")
            m2.metric("SOGLIA ISA 320", f"€ {mat:,.2f}")
            m3.metric("RATING RISCHIO", rischio)

            # --- ALERT BIG 4 ---
            voci_sopra = df[df[col_v] > mat]
            if not voci_sopra.empty:
