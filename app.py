import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 1. ARCHITETTURA VISIVA "ELITE AUDIT"
st.set_page_config(page_title="COIN-NEXUS | ELITE AUDIT", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&family=JetBrains+Mono&display=swap');
    .main { background: #05070a; color: #e2e8f0; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background: #0a0f18; border-right: 1px solid #1e293b; }
    .stMetric { 
        background: rgba(16, 24, 39, 0.8); 
        border: 1px solid #3b82f6; 
        border-radius: 12px; 
        padding: 20px !important;
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.1);
    }
    h1, h2, h3 { font-family: 'Inter', sans-serif; font-weight: 700; letter-spacing: -1px; }
    .status-tag { background: #3b82f6; color: white; padding: 4px 12px; border-radius: 50px; font-size: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. SISTEMA DI COMANDO SIDEBAR
st.sidebar.markdown("<h2 style='color: #3b82f6;'>COIN-NEXUS</h2><p style='color: #64748b; font-size: 12px;'>ELITE AUDIT SYSTEM v6.0</p>", unsafe_allow_html=True)

menu = st.sidebar.radio("SISTEMI DI ANALISI", [
    "💠 DASHBOARD STRATEGICA", 
    "⚖️ MATERIALITÀ & RISCHIO", 
    "🛡️ TEST CONTINUITÀ (ISA 570)", 
    "🌪️ SIMULAZIONE STRESS TEST"
])

uploaded_file = st.sidebar.file_uploader("📥 SINCRONIZZA FLUSSO DATI", type=['xlsx', 'csv'])

# --- MOTORE DATI (CON DEMO MODE INTELLIGENTE) ---
if uploaded_file:
    try:
        if uploaded_file.name.endswith('.xlsx'): df = pd.read_excel(uploaded_file, engine='openpyxl')
        else: df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='latin-1')
        df.columns = [str(c).upper().strip() for c in df.columns]
        is_demo = False
    except: is_demo = True
else:
    df = pd.DataFrame({
        'VOCE': ['Liquidità', 'Crediti Commerciali', 'Rimanenze', 'Immobilizzazioni', 'Debiti Fornitori', 'Finanziamenti'],
        'VALORE': [450000, 320000, 150000, 1200000, 210000, 450000]
    })
    is_demo = True

# ==========================================
# MODULO 1: DASHBOARD STRATEGICA
# ==========================================
if menu == "💠 DASHBOARD STRATEGICA":
    st.markdown(f"<h1>💠 Executive Control Center {'<span class="status-tag">DEMO MODE</span>' if is_demo else ''}</h1>", unsafe_allow_html=True)
    v_col = 'VALORE' if 'VAL
