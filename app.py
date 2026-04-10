import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime

# --- CONFIGURAZIONE INTERFACCIA TECHNO ---
st.set_page_config(page_title="COIN-NEXUS CYBER-AUDIT", layout="wide", page_icon="💎")

# CSS Professionale: Deep Black e Neon Blue
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #333; }
    div[data-testid="stMetricValue"] { color: #00d4ff !important; font-family: 'Courier New', monospace; font-size: 2.5rem !important; }
    .stMetric { background-color: #111; border: 1px solid #222; border-radius: 8px; padding: 20px; }
    .stButton>button { 
        background: transparent; color: #00d4ff; border: 1px solid #00d4ff; 
        transition: 0.3s; width: 100%; font-weight: bold; letter-spacing: 1px;
    }
    .stButton>button:hover { background: #00d4ff; color: #000; box-shadow: 0 0 15px #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE ANALISI ---
def analisi_benford(data):
    digits = data.abs().astype(str).str.extract('([1-9])')[0].dropna().astype(int)
    if digits.empty: return pd.DataFrame()
    obs = digits.value_counts(normalize=True).sort_index()
    exp = pd.Series({i: np.log10(1 + 1/i) for i in range(1, 10)})
    return pd.DataFrame({'Reale': obs, 'Atteso': exp}).fillna(0)

# --- GENERATORE REPORT BIG 4 STYLE ---
def genera_pdf_isa(totale, mat, samp, anomalie, note, studio):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Istituzionale
    pdf.set_fill_color(15, 23, 42)
    pdf.rect(0, 0, 210, 50, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(190, 30, studio.upper(), ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(190, 10, "Documentazione di Revisione Indipendente - ISA Italia Compliant", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(30)
    
    # Sezione 1: Opinion & Methodology
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. GIUDIZIO E FONDAMENTI DELLA REVISIONE", ln=True)
    pdf.set_font("Arial", '', 10)
    text = (f"In data {datetime.date.today().strftime('%d/%m/%Y')}, è stata eseguita l'analisi forense della massa monetaria. "
            "La materialità di pianificazione è stata determinata secondo il principio ISA 320.")
    pdf.multi_cell(0, 7, text)
    
    # Tabella Parametri
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(100, 10, "Indicatore", 1, 0, 'L', True); pdf.cell(90, 10, "Valore (EUR)", 1, 1, 'R', True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(100, 10, "Massa Monetaria Verificata", 1); pdf.cell(90, 10, f"{totale:,.2f}", 1, 1, 'R')
    pdf.cell(100, 10, "Materialità (PM)", 1); pdf.cell(90, 10, f"{mat:,.2f}", 1, 1, 'R')
    pdf.cell(100, 10, "Soglia Errore Trascurabile (SAMP)", 1); pdf.cell(90, 10, f"{samp:,.2f}", 1, 1, 'R')
    
    # Sezione 2: Key Audit Matters (KAM)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
