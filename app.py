import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime

# --- CONFIGURAZIONE PROFESSIONALE ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM AUDIT", layout="wide")

# CSS per un look Enterprise
st.markdown("""
    <style>
    .stMetric { background: #1e293b; border: 1px solid #3b82f6; border-radius: 10px; padding: 15px; }
    .stButton>button { background: #2563eb; color: white; width: 100%; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTORE PDF ANTI-CRASH ---
def genera_report_pdf(totale, mat, rischio, df_anomalie):
    # Usiamo 'latin-1' come standard per FPDF
    pdf = FPDF()
    pdf.add_page()
    
    # Header Blu Big 4 Style
    pdf.set_fill_color(30, 58, 138)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 22)
    pdf.cell(190, 25, "AUDIT REPORT - COIN-NEXUS", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(30)
    
    # Sintesi Risultati
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, "Indicatore di Revisione", 1, fill=False)
    pdf.cell(90, 10, "Valore", 1, ln=True)
    
    pdf.set_font("Arial", '', 11)
    # Sostituiamo il simbolo € con la parola Euro per evitare l'errore 0
    pdf.cell(100, 10, "Capitale Totale Analizzato", 1)
    pdf.cell(90, 10, f"Euro {totale:,.2f}", 1, ln=True)
    pdf.cell(100, 10, "Soglia di Materialita", 1)
    pdf.cell(90, 10, f"Euro {mat:,.2f}", 1, ln=True)
    pdf.cell(100, 10, "Livello di Rischio", 1)
    pdf.cell(90, 10, str(rischio), 1, ln=True)
    
    pdf.ln(10)
    
    # Tabella Dettaglio (Vero Valore Aggiunto)
    if not df_anomalie.empty:
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(180, 0, 0)
        pdf.cell(190, 10, "DETTAGLIO VOCI SOPRA SOGLIA", ln=True)
        pdf.ln(5)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(130, 8, "Voce / Descrizione", 1)
        pdf.cell(60, 8, "Importo (Euro)", 1, ln=True)
        
        pdf.set_font("Arial", '', 9)
        for i, row in
