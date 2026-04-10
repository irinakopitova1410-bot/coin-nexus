import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import io

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM", layout="wide")

# --- STILE ---
st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e2e8f0; }
    .stMetric { background: rgba(16, 24, 39, 0.8); border: 1px solid #3b82f6; border-radius: 12px; padding: 20px; }
    .stButton>button { background: linear-gradient(90deg, #3b82f6, #2563eb); color: white; width: 100%; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONE PDF SICURA ---
def genera_report_pdf(totale, mat, rischio):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "COIN-NEXUS PLATINUM - AUDIT REPORT", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, f"Massa monetaria analizzata: Euro {totale:,.2f}", ln=True)
    pdf.cell(200, 10, f"Soglia di Materialita (ISA 320): Euro {mat:,.2f}", ln=True)
    pdf.cell(200, 10, f"Livello di Rischio: {rischio}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, "Conclusioni: Analisi completata con successo secondo standard ISA 320.")
    return pdf.output()

# --- SIDEBAR E CARICAMENTO ---
st.sidebar.title("💠 COIN-NEXUS PLATINUM")
uploaded_file = st.sidebar.file_uploader("Sincronizza Dati", type=['xlsx', 'csv'])
if uploaded_file:
    try:
        # Lettura file
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
        
        # --- NUOVO MAPPING INTELLIGENTE (Risolve 'index out of range') ---
        cols = df.columns.tolist()
        
        # Cerchiamo la colonna dei VALORI (Saldo, Importo, ecc.)
        col_v_list = [c for c in cols if any(x in c.lower() for x in ['saldo', 'importo', 'euro', 'valore', 'totale'])]
        # Cerchiamo la colonna delle DESCRIZIONI (Voce, Conto, ecc.)
        col_c_list = [c for c in cols if any(x in c.lower() for x in ['desc', 'voce', 'conto', 'account', 'nominativo'])]

        if not col_v_list or not col_c_list:
            st.warning("⚠️ Non ho trovato colonne con nomi standard (Saldo, Descrizione).")
            st.info("Scegli manualmente le colonne da analizzare:")
            col_v = st.selectbox("Seleziona la colonna degli IMPORTI:", cols)
            col_c = st.selectbox("Seleziona la colonna delle DESCRIZIONI:", cols)
        else:
            col_v = col_v_list[0]
            col_c = col_c_list[0]
        
        # Pulizia numeri (rimuove € e spazi)
        df[col_v] = pd.to_numeric(df[col_v].astype(str).replace('[€, ]', '', regex=True), errors='coerce').fillna(0)
        # ---------------------------------------------------------------

        st.title("🛡️ Audit Intelligence & Forensic")
        
        # ... qui continua il resto del codice delle metriche ...
        # Pulizia numeri
        df[col_v] = pd.to_numeric(df[col_v].astype(str).replace('[€, ]', '', regex=True), errors='coerce').fillna(0)

        st.title("🛡️ Audit Intelligence & Forensic")

        # Metriche
        totale = df[col_v].sum()
        mat = totale * 0.01
        rischio = "BASSO" if totale < 1000000 else "MODERATO"

        m1, m2, m3 = st.columns(3)
        m1.metric("CAPITALE ANALIZZATO", f"€ {totale:,.2f}")
        m2.metric("MATERIALITÀ (ISA 320)", f"€ {mat:,.2f}")
        m3.metric("STATUS", rischio)

        # --- ALERT BIG 4 (RIGA 65) ---
        voci_pericolose = df[df[col_v] > mat]
        if not voci_pericolose.empty:
            st.error(f"🚨 ALERT: Rilevate {len(voci_pericolose)} voci sopra la materialità!")
            st.dataframe(voci_pericolose[[col_c, col_v]].sort_values(by=col_v, ascending=False))

        # Visualizzazione
        st.subheader("📊 Mappa Concentrazione")
        fig = px.treemap(df.nlargest(20, col_v), path=[col_c], values=col_v, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        # Download Report
        st.divider()
        if st.button("🚀 GENERA REPORT PDF"):
            pdf_out = genera_report_pdf(totale, mat, rischio)
            st.download_button(label="Clicca qui per scaricare", data=bytes(pdf_out), file_name="Audit_Platinum.pdf", mime="application/pdf")

    except Exception as e:
        st.error(f"⚠️ Errore durante l'analisi: {e}")
else:
    st.info("👋 Carica un file per iniziare.")
