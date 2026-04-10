import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime

# --- CONFIGURAZIONE UI TECHNO ---
st.set_page_config(page_title="COIN-NEXUS ULTIMATE", layout="wide", page_icon="💎")

# CSS "Cyber-Audit" per un look da 100k
st.markdown("""
    <style>
    .stApp { background-color: #050508; color: #e0e6ed; }
    [data-testid="stSidebar"] { background-color: #0a0b14; border-right: 1px solid #1f293a; }
    
    /* Metriche Futuristiche */
    div[data-testid="stMetricValue"] { color: #00d4ff !important; font-family: 'Courier New', monospace; font-size: 2.2rem !important; }
    .stMetric { background-color: #101423; border: 1px solid #1f293a; border-radius: 10px; padding: 15px; box-shadow: 0 4px 15px rgba(0,212,255,0.1); }
    
    /* Pulsante ad alto impatto */
    .stButton>button {
        background: linear-gradient(90deg, #1e40af, #3b82f6);
        color: white; border: none; width: 100%; font-weight: bold; border-radius: 5px;
        text-transform: uppercase; letter-spacing: 1px; transition: 0.3s;
    }
    .stButton>button:hover { box-shadow: 0 0 20px rgba(59, 130, 246, 0.6); transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONI DI ANALISI ---
def test_benford(data):
    try:
        digits = data.abs().astype(str).str.extract('([1-9])')[0].dropna().astype(int)
        if digits.empty: return pd.DataFrame()
        obs = digits.value_counts(normalize=True).sort_index()
        exp = pd.Series({i: np.log10(1 + 1/i) for i
