import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import io

# 1. SETUP ESTETICO ELITE
st.set_page_config(page_title="COIN-NEXUS ELITE", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e2e8f0; }
    [data-testid="stSidebar"] { background-color: #0a0f18; border-right: 1px solid #1e293b; }
    .stMetric { 
        background: rgba(16, 24, 39, 0.7); 
        border: 1px solid #3b82f6; 
        border-radius: 15px; padding: 20px;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
    }
    .stButton>button { 
        background: linear-gradient(90deg, #3b82f6, #2563eb); 
        color: white; border-radius: 8px; font-weight: bold; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNZIONI CORE (IL "CERVELLO")
def smart_mapping(df):
    """Identifica le colonne chiave indipendentemente dal nome."""
    cols = df.columns
    mapping = {}
    
    # Cerca Valore/Importo
    v_search = ['valore', 'saldo', 'importo', 'amount', 'euro', 'bilancio']
    mapping['valore'] = [c for c in cols if any(x in c.lower() for x in v_search)][0]
    
    # Cerca Descrizione/Voce
    d_search = ['voce', 'descrizione', 'conto', 'account', 'item']
    mapping['desc'] = [c for c in cols if any(x in c.lower() for x in d_search)][0]
    
    return mapping

def benford_test(series):
    """Test anti-frode ISA 240."""
    digits = series.astype(str).str.extract(r'([1-9])')[0].dropna().astype(int)
    if digits.empty: return None, None
    actual = digits.value_counts(normalize=True).sort_index()
    expected = pd.Series({d: np.log10(1 + 1/d) for d in range(1, 10)})
    return actual, expected

# 3. SIDEBAR NAVIGATION
st.sidebar.title("COIN-NEXUS ELITE")
mode = st.sidebar.selectbox("COMMAND CENTER", ["🛡️ AUDIT & FORENSIC", "💎 RATING BASILEA IV", "🌪️ STRESS TEST"])
file = st.sidebar.file_uploader("Sincronizza Dataset", type=['csv', 'xlsx'])

# 4. MODULO 1: AUDIT & FORENSIC
if mode == "🛡️ AUDIT & FORENSIC":
    st.title("🛡️ Audit Intelligence & Forensic Analysis")
    
    if file:
        df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
        m = smart_mapping(df)
        df[m['valore']] = pd.to_numeric(df[m['valore']], errors='coerce').fillna(0)
        
        # LOGICA BIG 4: Materialità ISA 320
        totale = df[m['valore']].sum()
        materiality = totale * 0.005 # 0.5% (Prudenziale)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("CAPITALE ANALIZZATO", f"€ {totale:,.0f}")
        c2.metric("MATERIALITÀ (ISA 320)", f"€ {materiality:,.0f}", "Soglia Errore")
        c3.metric("ALERT LIVELLO", "HIGH" if (df[m['valore']] > materiality).any() else "LOW")

        # Visualizzazione Asset
        st.subheader("📊 Esposizione Masse Patrimoniali")
        fig = px.treemap(df.nlargest(25, m['valore']), path=[m['desc']], values=m['valore'], 
                         color=m['valore'], color_continuous_scale='Blues', template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        # Forensic Analysis
        st.subheader("🕵
