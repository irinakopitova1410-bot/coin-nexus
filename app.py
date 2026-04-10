import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime

# --- CONFIGURAZIONE UI TECHNO ---
st.set_page_config(page_title="COIN-NEXUS CYBER-AUDIT", layout="wide")

# CSS "Cyber-Dark" Ultra-Stabile
st.markdown("""
    <style>
    .stApp { background-color: #050508; color: #e0e6ed; }
    [data-testid="stSidebar"] { background-color: #0a0b14; border-right: 1px solid #1f293a; }
    div[data-testid="stMetricValue"] { color: #3b82f6 !important; font-family: 'Courier New', monospace; font-size: 1.8rem !important; }
    .stMetric { background-color: #101423; border: 1px solid #1f293a; border-radius: 10px; padding: 15px; }
    .stButton>button { background: linear-gradient(90deg, #1e40af, #3b82f6); color: white; border: none; width: 100%; font-weight: bold; border-radius: 5px; }
    .stTabs [data-baseweb="tab-list"] { background-color: #0a0b14; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONI DI SUPPORTO ---
def safe_benford(data):
    try:
        digits = data.abs().astype(str).str.extract('([1-9])')[0].dropna().astype(int)
        if digits.empty: return pd.DataFrame()
        obs = digits.value_counts(normalize=True).sort_index()
        exp = pd.Series({i: np.log10(1 + 1/i) for i in range(1, 10)})
        return pd.DataFrame({'Reale': obs, 'Atteso': exp}).fillna(0)
    except:
        return pd.DataFrame()

def genera_pdf_safe(massa, mat, anom, studio):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(15, 23, 42)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 22)
    pdf.cell(190, 25, studio.upper(), ln=True, align='C')
    pdf.set_text_color(0, 0, 0)
    pdf.ln(30)
