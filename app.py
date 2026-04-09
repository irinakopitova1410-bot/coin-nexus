import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF

# --- CONFIGURAZIONE INTERFACCIA ELITE ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e2e8f0; }
    .stMetric { background: rgba(16, 24, 39, 0.8); border: 1px solid #3b82f6; border-radius: 12px; padding: 20px; }
    .stButton>button { background: linear-gradient(90deg, #3b82f6, #2563eb); color: white; border: none; font-weight: bold; width: 100%; }
    h1, h2, h3 { color: #f8fafc; font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONI SCIENTIFICHE ---
def benford_analysis(data):
    """Rileva manipolazioni contabili."""
    digits = data.astype(str).str.extract(r'([1-9])')[0].dropna().astype(int)
    if digits.empty: return None, None
    actual = digits.value_counts(normalize=True).sort_index()
    expected = pd.Series({d: np.log10(1 + 1/d) for d in range(1, 10)})
    return actual, expected

def altman_z_score(ca, ct, ut, mon, pfn, ricavi):
    """Previsione insolvenza (Z-Score)."""
    # Formula semplificata per aziende private
    z = (1.2 * (ca/ct)) + (1.4 * (ut/ct)) + (3.3 * (mon/ct)) + (0.6 * (pfn/ct)) + (1.0 * (ricavi/ct))
    return z

# --- SIDEBAR & NAVIGATION ---
st.sidebar.title("💠 COIN-NEXUS PLATINUM")
st.sidebar.markdown("---")
mode = st.sidebar.selectbox("PILOT CENTER", ["🛡️ AUDIT & FORENSIC", "📈 RISK PREDICTION", "⚖️ LEGAL REPORT"])
file = st.sidebar.file_uploader("Upload Financial Dataset", type=['csv', 'xlsx'])

if file:
    try:
        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        cols = df.columns.tolist()

        if mode == "🛡️ AUDIT & FORENSIC":
            st.title("🛡️ Audit Intelligence Engine")
            
            # Smart Mapping
            c1, c2 = st.columns(2)
            def_v = [c for c in cols if any(x in c.
