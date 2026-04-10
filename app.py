import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime

# --- CONFIGURAZIONE UI TECHNO ---
st.set_page_config(page_title="COIN-NEXUS CYBER-AUDIT", layout="wide")

# CSS "Cyber-Dark" stabile
st.markdown("""
    <style>
    .stApp { background-color: #0a0b10; color: #e0e6ed; }
    [data-testid="stSidebar"] { background-color: #0e1117; border-right: 1px solid #1f2937; }
    
    /* Stile Metriche Techno */
    div[data-testid="stMetricValue"] { color: #3b82f6 !important; font-family: 'Courier New', monospace; }
    .stMetric { 
        background-color: #161b22; 
        border: 1px solid #30363d; 
        border-radius: 10px; 
        padding: 15px;
    }
    
    /* Pulsante Techno */
    .stButton>button {
        background: linear-gradient(90deg, #1d4ed8, #3b82f6);
        color: white;
        border: none;
        border-radius: 5px;
        font-weight: bold;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGICA DI ANALISI ---
def test_benford(data):
    # Estrae la prima cifra in modo sicuro
    digits = data.abs().astype(str).str.extract('([1-9])')[0].dropna().astype(int)
    if digits.empty: return pd.DataFrame()
    obs = digits.value_counts(normalize=True).sort_index()
    exp =
