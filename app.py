import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM", layout="wide")

# --- FUNZIONE GENERAZIONE PDF ---
def genera_report_pdf(totale, mat, rischio, df_anomalie):
    pdf = FPDF()
    pdf.add_page()
    
    # Intestazione Blu
    pdf.set_fill_color(30, 58, 138)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(190, 25, "COIN-NEXUS PLATINUM REPORT", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(25)
    
    # Metriche principali
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, "Parametro di Revisione", 1)
    pdf.cell(90, 10, "Valore Rilevato", 1, ln=True)
    
    pdf.set_font("Arial", '', 11)
    pdf.cell(100, 10, "Massa Monetaria Analizzata", 1)
    pdf.cell(90, 10, f"Euro {totale:,.2f}", 1, ln=True)
    pdf.cell(100, 10, "Soglia Materialita (ISA 320)", 1)
    pdf.cell(90, 10, f"Euro {mat:,.2f}", 1, ln=True)
    pdf.cell(100, 10, "Rating di Rischio", 1)
    pdf.cell(90, 10, str(rischio), 1, ln=True)
    
    pdf.ln(10)
    
    # Tabella Anomalie
    if not df_anomalie.empty:
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(200, 0, 0)
        pdf.cell(190, 10, "DETTAGLIO VOCI SOPRA SOGLIA", ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(140, 8, "Descrizione", 1)
        pdf.cell(50, 8, "Importo", 1, ln=True)
        
        pdf.set_font("Arial", '', 9)
        for i, row in df_anomalie.head(20).iterrows():
            # Codifica per evitare l'errore '0' dei caratteri speciali
            desc_pulita = str(row[0]).encode('latin-1', 'ignore').decode('latin-1')
            pdf.cell(140, 7, desc_pulita[:65], 1)
            pdf.cell(50, 7, f"{row[1]:,.2f}", 1, ln=True)
