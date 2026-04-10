import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime

# 1. Configurazione Iniziale
st.set_page_config(page_title="COIN-NEXUS PLATINUM", layout="wide")

# 2. Funzione PDF Semplificata e Robusta
def genera_report_pdf(totale, mat, rischio, df_anomalie):
    pdf = FPDF()
    pdf.add_page()
    
    # Intestazione Professionale
    pdf.set_fill_color(30, 58, 138)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(190, 25, "AUDIT REPORT - COIN-NEXUS PLATINUM", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(30)
    
    # Dati Sintetici
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, "Indicatore", 1)
    pdf.cell(90, 10, "Valore", 1, ln=True)
    
    pdf.set_font("Arial", '', 11)
    pdf.cell(100, 10, "Massa Analizzata", 1)
    pdf.cell(90, 10, f"{totale:,.2f}", 1, ln=True)
    pdf.cell(100, 10, "Rating Rischio", 1)
    pdf.cell(90, 10, str(rischio), 1, ln=True)
    
    pdf.ln(10)
    
    # Tabella Anomalie (Prime 15 voci per non appesantire)
    if not df_anomalie.empty:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(140, 8, "Voce di Bilancio", 1)
        pdf.cell(50, 8, "Importo", 1, ln=True)
        
        pdf.set_font("Arial", '', 9)
        for i, row in df_anomalie.head(15).iterrows():
            # Pulizia testo per evitare Syntax/Encoding Error
            testo_pulito = str(row[0]).encode('ascii', 'ignore').decode('ascii')
            pdf.cell(140, 7, testo_pulito[:60], 1)
            pdf.cell(50, 7, f"{row[1]:,.2f}", 1, ln=True)
            
    return pdf.output()

# 3. Interfaccia Utente
st.title("🛡️ Coin-Nexus Audit Platinum")

file = st.sidebar.file_uploader("Carica File Excel o CSV", type=['xlsx', 'csv'])

if file:
    try:
        # Caricamento Dati
        if file.name.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            df = pd.read_csv(file)
            
        # Individuazione Colonne
        col_v = df.select_dtypes(include=[np.number]).columns[0]
        col_c = df.columns[0]
        
        # Analisi Audit
        totale = df[col_v].sum()
        mat = totale * 0.015
        anomalie = df[df[col_v] > mat].sort_values(by=col_v, ascending=False)
        rischio = "ALTO" if len(anomalie) > 0 else "CONTROLLATO"

        # Visualizzazione
        c1, c2 = st.columns(2)
        c1.metric("MASSA TOTALE", f"€ {totale:,.2f}")
        c2.metric("RISCHIO", rischio)

        st.plotly_chart(px.treemap(df.nlargest(15, col_v), path=[col_c], values=col_v, template="plotly_dark"), use_container_width=True)

        # Bottone Report
        if st.button("🚀 SCARICA CERTIFICAZIONE PDF"):
            pdf_data = genera_report_pdf(totale, mat, rischio, anomalie)
            # Gestione universale output PDF
            pdf_bytes = bytes(pdf_data) if isinstance(pdf_data, (bytes, bytearray)) else pdf_data
            
            st.download_button(
                label="📥 Clicca qui per il Download",
                data=pdf_bytes,
                file_name="Audit_Platinum.pdf",
                mime="application/pdf"
            )
            st.success("Report Generato!")

    except Exception as e:
        st.error(f"Errore nel file: {e}")
else:
    st.info("Carica un file per iniziare l'analisi.")
