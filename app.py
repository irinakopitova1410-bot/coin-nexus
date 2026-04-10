
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM", layout="wide")

# --- FUNZIONE PDF CORRETTA (Senza .encode) ---
def genera_report_pdf(totale, mat, rischio):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "COIN-NEXUS PLATINUM - AUDIT CERTIFICATION", ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(200, 10, f"Data: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "SINTESI ANALISI:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(200, 8, f"- Massa Monetaria: Euro {totale:,.2f}", ln=True)
    pdf.cell(200, 8, f"- Soglia Materialita: Euro {mat:,.2f}", ln=True)
    pdf.cell(200, 8, f"- Rischio Rilevato: {rischio}", ln=True)
    
    # Restituisce i byte direttamente (fpdf2 output() è già un bytearray/bytes)
    return pdf.output()

# --- INTERFACCIA ---
st.sidebar.title("💠 COIN-NEXUS PLATINUM")
uploaded_file = st.sidebar.file_uploader("Carica File", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        
        # Mapping Colonne
        cols = [str(c) for c in df.columns]
        col_v = next((c for c in cols if any(x in c.lower() for x in ['saldo', 'importo', 'euro', 'valore', 'amount'])), cols[0])
        col_c = next((c for c in cols if any(x in c.lower() for x in ['desc', 'voce', 'conto', 'nominativo', 'account'])), cols[1] if len(cols)>1 else cols[0])

        # Pulizia numeri
        df[col_v] = pd.to_numeric(df[col_v].astype(str).replace('[€, ]', '', regex=True), errors='coerce').fillna(0)

        st.title("🛡️ Audit Intelligence")

        totale = df[col_v].sum()
        mat = totale * 0.015
        rischio = "ALTO" if (df[col_v] > mat).any() else "CONTROLLATO"

        c1, c2, c3 = st.columns(3)
        c1.metric("TOTALE ANALIZZATO", f"€ {totale:,.2f}")
        c2.metric("SOGLIA ISA 320", f"€ {mat:,.2f}")
        c3.metric("RATING", rischio)

        # Alert
        voci_critiche = df[df[col_v] > mat]
        if not voci_critiche.empty:
            st.error(f"🚨 Rilevate {len(voci_critiche)} anomalie sopra soglia!")
            st.dataframe(voci_critiche[[col_c, col_v]])

        # Treemap
        st.plotly_chart(px.treemap(df.nlargest(20, col_v), path=[col_c], values=col_v, template="plotly_dark"), use_container_width=True)

        # REPORT PDF (Fix finale)
        st.divider()
        if st.button("🚀 GENERA REPORT PDF"):
            pdf_bytes = genera_report_pdf(totale, mat, rischio)
            # Trasformiamo in bytes se fpdf2 restituisce bytearray
            st.download_button(
                label="📥 Scarica Report",
                data=bytes(pdf_bytes), 
                file_name="Audit_Report.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"Errore tecnico: {e}")
else:
    st.info("Carica un file Excel per iniziare.")
