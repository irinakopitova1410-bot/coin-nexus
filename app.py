import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime

# --- CONFIGURAZIONE ELITE ---
st.set_page_config(page_title="COIN-NEXUS ULTIMATE", layout="wide", page_icon="💎")

st.markdown("""
    <style>
    .main { background: #0b0e14; }
    .stMetric { background: #111827; border-left: 5px solid #3b82f6; border-radius: 5px; padding: 20px; }
    .stSidebar { background-color: #111827; }
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE ANALISI AVANZATA ---
def analisi_benford(data):
    digits = data.abs().astype(str).str.extract('([1-9])')[0].dropna().astype(int)
    if digits.empty: return pd.DataFrame()
    obs = digits.value_counts(normalize=True).sort_index()
    exp = pd.Series({i: np.log10(1 + 1/i) for i in range(1, 10)})
    return pd.DataFrame({'Reale': obs, 'Atteso': exp}).fillna(0)

# --- GENERATORE CARTE DI LAVORO (PDF CERTIFICATO ISA) ---
def genera_pdf_professional(totale, mat, samp, rischio, anomalie, note, studio_nome):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Branding Istituzionale
    pdf.set_fill_color(30, 58, 138)
    pdf.rect(0, 0, 210, 55, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(190, 30, studio_nome.upper(), ln=True, align='C')
    pdf.set_font("Arial", 'I', 11)
    pdf.cell(190, 10, "Documentazione di Revisione ai sensi dei principi ISA Italia 230 e 320", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(30)
    
    # 1. OBBIETTIVI E RESPONSABILITÀ (ISA 230)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. OBBIETTIVI DELL'ANALISI E RESPONSABILITÀ", ln=True)
    pdf.set_font("Arial", '', 10)
    paragraph_responsability = (
        "La presente documentazione costituisce una carta di lavoro automat
