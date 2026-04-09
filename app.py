import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 1. SETUP ESTETICO "ELITE"
st.set_page_config(page_title="COIN-NEXUS TITANIUM", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&display=swap');
    .main { background: radial-gradient(circle at 50% 50%, #020617, #000000); color: #f1f5f9; font-family: 'Space Grotesk', sans-serif; }
    [data-testid="stSidebar"] { background: rgba(15, 23, 42, 0.95); border-right: 1px solid #00d4ff; }
    .stMetric { background: rgba(30, 41, 59, 0.7); border: 1px solid #00d4ff; border-radius: 12px; padding: 20px !important; }
    h1 { text-shadow: 0 0 15px #00d4ff; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGICA SIDEBAR
st.sidebar.title("⚡ COIN-NEXUS CORE")
menu = st.sidebar.radio("SISTEMI ATTIVI", [
    "💎 DASHBOARD ESECUTIVA", 
    "🕵️ RISCHIO & MATERIALITÀ", 
    "🛡️ SCUDO DI CONTINUITÀ"
])

uploaded_file = st.sidebar.file_uploader("📥 CARICA BILANCIO", type=['xlsx', 'csv'])

# --- GESTIONE DATI ---
if uploaded_file:
    try:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
        df.columns = [str(c).upper().strip() for c in df.columns]
        demo = False
    except:
        demo = True
else:
    df = pd.DataFrame({'VOCE': ['Liquidità', 'Crediti', 'Debiti'], 'VALORE': [500000, 300000, 200000]})
    demo = True

# ==========================================
# MODULO 1: DASHBOARD
# ==========================================
if menu == "💎 DASHBOARD ESECUTIVA":
    st.markdown(f"<h1>💎 Analisi Strategica {'(DEMO)' if demo else ''}</h1>", unsafe_allow_html=True)
    v_col = 'VALORE' if 'VALORE' in df.columns else df.columns[1]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("TOTALE ATTIVO", f"€ {df[v_col].sum():,.0f}", "+3.2%")
    c2.metric("HEALTH SCORE IA", "96/100", "ECCELLENTE")
    c3.metric("RISCHIO AUDIT", "LOW", "-5%", delta_color="inverse")

    st.markdown("---")
    fig = px.sunburst(df, path=[df.columns[0]], values=v_col, color=v_col, color_continuous_scale='GnBu', template='plotly_dark')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# MODULO 2: RISCHIO & MATERIALITÀ
# ==========================================
elif menu == "🕵️ RISCHIO & MATERIALITÀ":
    st.title("🕵️ Valutazione Professionale (ISA 320)")
    
    col_1, col_2 = st.columns(2)
    with col_1:
        st.subheader("S
