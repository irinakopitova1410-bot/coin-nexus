import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime

# --- CONFIGURAZIONE INTERFACCIA ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM AUDIT", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e2e8f0; }
    .stMetric { background: rgba(16, 24, 39, 0.8); border: 1px solid #3b82f6; border-radius: 12px; padding: 20px; }
    .stButton>button { background: linear-gradient(90deg, #3b82f6, #2563eb); color: white; border-radius: 8px; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONE GENERAZIONE PDF PROFESSIONALE ---
def genera_report_pdf(totale, mat, rischio, df_anomalie):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Blu Istituzionale (Valore +200%)
    pdf.set_fill_color(30, 58, 138)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(190, 25, "COIN-NEXUS PLATINUM - AUDIT REPORT", ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(190, -5, f"Generato il: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
