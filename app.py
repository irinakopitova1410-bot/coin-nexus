import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime

# --- SETUP ESTETICO PREMIUM ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM AUDIT", layout="wide")

st.markdown("""
    <style>
    .stMetric { background: #111827; border: 1px solid #3b82f6; border-radius: 12px; padding: 20px; }
    .stButton>button { background: linear-gradient(90deg, #1d4ed8, #3b82f6); color: white; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTORE PDF ULTRA-STABILE ---
class AuditPDF(FPDF):
    def header(self):
        self.set_fill_color(30, 58, 138)
        self.rect(0, 0, 210, 40, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", 'B', 22)
        self.cell(190, 25, "AUDIT REPORT CERTIFIED", ln=True, align='C')
        self.ln(10)

def genera_report_pdf(totale, mat, rischio, df_anomalie):
    pdf = AuditPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Sintesi Metriche
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "SINTESI DELLE EVIDENZE", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", '', 11)
    # Protezione caratteri: usiamo stringhe pulite
    pdf.cell(100, 10, "Massa Analizzata:", 1)
    pdf.cell(90, 10, f"Euro {totale:,.2f}", 1, ln=True)
    pdf.cell(100, 10, "Soglia Materialita (ISA 320):", 1)
    pdf.cell(90, 10, f"Euro {mat:,.2f}", 1, ln=True)
    pdf.cell(100, 10, "Rating Rischio Complessivo:", 1)
    pdf.cell(90, 10, str(rischio), 1, ln=True)
