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
    .main { background: #0b1117; }
    .stMetric { background: #161b22; border-top: 4px solid #3b82f6; border-radius: 8px; padding: 20px; }
    .stAlert { border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONI DI ANALISI AVANZATA ---
def check_data_quality(df, col_v):
    """Modulo di Integrità Dati"""
    issues = []
    if df[col_v].isnull().any(): issues.append(f"Rilevati {df[col_v].isnull().sum()} valori mancanti.")
    if (df[col_v] == 0).any(): issues.append(f"Rilevate { (df[col_v] == 0).sum() } righe con valore zero.")
    if (df[col_v] < 0).any(): issues.append("Rilevati valori negativi (possibili storni o errori di segno).")
    return issues

def benford_analysis(data):
    digits = data.abs().astype(str).str.extract('([1-9])')[0].dropna().astype(int)
    if digits.empty: return pd.DataFrame()
    obs = digits.value_counts(normalize=True).sort_index()
    exp = pd.Series({i: np.log10(1 + 1/i) for i in range(1, 10)})
    return pd.DataFrame({'Reale': obs, 'Atteso': exp}).fillna(0)

# --- ENGINE REPORTING ---
def genera_pdf_platinum(totale, mat, samp, rischio, anomalie, note, studio, quality_report):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Istituzionale
    pdf.set_fill_color(22, 27, 34)
    pdf.rect(0, 0, 210, 50, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(190, 30, studio.upper(), ln=True, align='C')
    pdf.set
