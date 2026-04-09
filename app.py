import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 1. ARCHITETTURA TITANIUM (STILE BIG4)
st.set_page_config(page_title="COIN-NEXUS TITANIUM", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&family=Inter:wght@400;700&display=swap');
    .main { background: radial-gradient(circle at 50% 50%, #020617, #000000); color: #f1f5f9; font-family: 'Space Grotesk', sans-serif; }
    [data-testid="stSidebar"] { background: rgba(15, 23, 42, 0.95); backdrop-filter: blur(20px); border-right: 1px solid #00d4ff; }
    .stMetric { background: rgba(30, 41, 59, 0.7); border: 1px solid #00d4ff; border-radius: 15px; padding: 25px !important; box-shadow: 0 0 20px rgba(0, 212, 255, 0.2); }
    h1 { text-shadow: 0 0 15px #00d4ff; color: #ffffff; letter-spacing: -1px; }
    .stButton>button { background: linear-gradient(90deg, #00d4ff, #005f73); color: white; border: none; border-radius: 10px; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# 2. MENU ESECUTIVO
st.sidebar.markdown("<h2 style='color: #00d4ff;'>⚡ COIN-NEXUS</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio("MODULI REVISIONE", [
    "💎 DASHBOARD ESECUTIVA", 
    "🕵️ RISCHIO & MATERIALITÀ", 
    "🛡️ SCUDO DI CONTINUITÀ", 
    "📊 PROIEZIONI CASH-FLOW"
])

uploaded_file = st.sidebar.file_uploader("📥 CARICA DATASET BILANCIO", type=['xlsx', 'csv'])

# --- GESTIONE DATI ---
if uploaded_file:
    try:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
        df.columns = [str(c).upper() for c in df.columns]
        demo = False
    except:
        demo = True
else:
    df = pd.DataFrame({
        'VOCE': ['Liquidità', 'Crediti', 'Immobilizzazioni', 'Debiti', 'Patrimonio'], 
        'VALORE': [450000, 320000, 800000, 250000, 1320000]
    })
    demo = True

# ==========================================
# MODULO 1: DASHBOARD ESECUTIVA
# ==========================================
