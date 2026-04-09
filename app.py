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
    .stMetric { background: #0a0f18; border: 1px solid #3b82f6; border-radius: 10px; padding: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONI DI SUPPORTO ---
def get_pdf_download_link(totale, mat):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "COIN-NEXUS PLATINUM REPORT", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Totale Analizzato: {totale:,.2f} EUR", ln=True)
    pdf.cell(200, 10, f"Materialita (ISA 320): {mat:,.2f} EUR", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- SIDEBAR ---
st.sidebar.title("💠 COIN-NEXUS PLATINUM")
menu = st.sidebar.selectbox("MODULO", ["AUDIT INTELLIGENCE", "BASILEA IV", "STRESS TEST"])
uploaded_file = st.sidebar.file_uploader("Carica Excel o CSV", type=['csv', 'xlsx'])

# --- LOGICA PRINCIPALE ---
if uploaded_file:
    try:
        # Caricamento universale
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
        else:
            df = pd.read_excel(uploaded_file)

        if menu == "AUDIT INTELLIGENCE":
            st.title("🛡️ Audit Intelligence Engine")
            
            # Mappatura con paracadute: se non la trova, la chiede all'utente
            col_nomi = df.columns.tolist()
            
            st.subheader("⚙️ Configurazione Colonne")
            c_select, v_select = st.columns(2)
            
            # Tentativo di auto-selezione
            def_v = [c for c in col_nomi if any(x in c.lower() for x in ['valore', 'importo', 'saldo', 'total', 'euro']) ]
            def_c = [c for c in col_nomi if any(x in c.lower() for x in ['voce', 'descrizione', 'conto', 'account', 'item']) ]
            
            col_v = v_select.selectbox("Seleziona Colonna Valori (Numeri)", col_nomi, index=col_nomi.index(def_v[0]) if def_v else 0)
            col_c = c_select.selectbox("Seleziona Colonna Descrizione (Testo)", col_nomi, index=col_nomi.index(def_c[0]) if def_c else 0)

            # Pulizia dati
            df[col_v] = pd.to_numeric(df[col_v].astype(str).replace('[€, ]', '', regex=True), errors='coerce').fillna(0)

            # Calcoli ISA 320
            totale_massa = df[col_v].sum()
            materiality = totale_massa * 0.01

            # Dashboard
            m1, m2, m3 = st.columns(3)
            m1.metric("CAPITALE TOTALE", f"€ {totale_massa:,.2f}")
            m2.metric("MATERIALITÀ (1%)", f"€ {materiality:,.2f}")
            m3.metric("ALERT LIVELLO", "⚠️ RISCHIO" if (df[col_v] > materiality).any() else "✅ OK")

            # Grafico
            fig = px.treemap(df.nlargest(20, col_v), path=[col_c], values=col_v, color=col_v, color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)

            # Report
            if st.button("📥 Genera Report Platinum"):
                pdf_bytes = get_pdf_download_link(totale_massa, materiality)
                st.download_button("Scarica PDF", pdf_bytes, "Audit_Report.pdf")

        elif menu == "BASILEA IV":
            st.title("💎 Rating Avanzato")
            ebitda = st.number_input("EBITDA", value=1000.0)
            pfn = st.number_input("PFN (Debito)", value=3000.0)
            st.metric("RATIO PFN/EBITDA", round(pfn/ebitda, 2) if ebitda != 0 else 0)

    except Exception as e:
        st.error(f"Errore nel caricamento: {e}")
else:
    st.info("👋 Benvenuto. Carica un file Excel o CSV per iniziare l'analisi.")
