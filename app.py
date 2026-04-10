import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime

# --- CONFIGURAZIONE INTERFACCIA ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM", layout="wide")

# Funzione PDF corretta per FPDF2 (Alta Stabilità)
def genera_report_pdf(totale, mat, rischio, df_anomalie):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Blu Professionale
    pdf.set_fill_color(30, 58, 138)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(190, 25, "AUDIT REPORT CERTIFIED - COIN-NEXUS", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(30)
    
    # Tabelle Riepilogo
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, "Indicatore", 1)
    pdf.cell(90, 10, "Valore rilevato", 1, ln=True)
    
    pdf.set_font("Arial", '', 11)
    pdf.cell(100, 10, "Massa Analizzata", 1)
    pdf.cell(90, 10, f"Euro {totale:,.2f}", 1, ln=True)
    pdf.cell(100, 10, "Rating Rischio", 1)
    pdf.cell(90, 10, str(rischio), 1, ln=True)
    
    pdf.ln(10)
    
    # Tabella Anomalie (Il cuore del valore +200%)
    if not df_anomalie.empty:
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(180, 0, 0)
        pdf.cell(0, 10, "ECCEZIONI SOPRA SOGLIA DI MATERIALITA", ln=True)
        pdf.ln(5)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(140, 8, "Voce / Conto", 1)
        pdf.cell(50, 8, "Importo", 1, ln=True)
        
        pdf.set_font("Arial", '', 9)
        for i, row in df_anomalie.head(20).iterrows():
            # Pulizia per evitare l'errore 0 (Encoding Safe)
            txt = str(row[0]).encode('ascii', 'ignore').decode('ascii')
            pdf.cell(140, 7, txt
