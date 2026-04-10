import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM", layout="wide")

# Funzione Report PDF Professionale
def genera_report_pdf(totale, mat, rischio, num_voci):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "COIN-NEXUS PLATINUM - AUDIT CERTIFICATION", ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(200, 10, f"Data Analisi: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "SINTESI DEI RISULTATI:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(200, 8, f"- Massa Monetaria Totale: Euro {totale:,.2f}", ln=True)
    pdf.cell(200, 8, f"- Soglia Materialita (ISA 320): Euro {mat:,.2f}", ln=True)
    pdf.cell(200, 8, f"- Grado di Rischio Rilevato: {rischio}", ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 8, "Conformita: L'analisi statistica e stata eseguita su dataset digitale. Le voci sopra soglia richiedono verifica documentale immediata.")
    return pdf.output()

# --- INTERFACCIA ---
st.sidebar.title("💠 COIN-NEXUS PLATINUM")
st.sidebar.markdown("---")
uploaded_file = st.sidebar.file_uploader("Sincronizza Database Aziendale", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        # Caricamento
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        
        # Pulizia colonne
        cols = [str(c) for c in df.columns]
        
        # Ricerca Automatica Colonne
        col_v = next((c for c in cols if any(x in c.lower() for x in ['saldo', 'importo', 'valore', 'euro', 'amount'])), None)
        col_c = next((c for c in cols if any(x in c.lower() for x in ['desc', 'voce', 'conto', 'nominativo', 'account'])), None)

        if not col_v or not col_c:
            st.error("❌ Non riesco a trovare le colonne 'Importo' e 'Descrizione'. Selezionale a mano:")
            col_v = st.selectbox("Seleziona colonna dei SOLDI:", cols)
            col_c = st.selectbox("Seleziona colonna dei NOMI:", cols)
        
        # Conversione Numerica
        df[col_v] = pd.to_numeric(df[col_v].astype(str).replace('[€, ]', '', regex=True), errors='coerce').fillna(0)

        # --- LOGICA AUDIT ---
        st.title("🛡️ Dashboard Audit & Forensic Intelligence")
        
        totale = df[col_v].sum()
        mat = totale * 0.015  # 1.5% Materialità standard
        rischio_final = "ALTO" if (df[col_v] > mat).any() else "BASSO"

        # Widget Metriche
        m1, m2, m3 = st.columns(3)
        m1.metric("CAPITALE ANALIZZATO", f"€ {totale:,.2f
