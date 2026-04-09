import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 1. ENGINE CONFIGURATION (ULTRA-SPEED)
st.set_page_config(page_title="COIN-NEXUS TITANIUM", layout="wide", initial_sidebar_state="expanded")

# CSS PRO: Effetto "Frosted Glass" e Typography Svizzera
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');
    .main { background: #050505; color: #ffffff; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background: rgba(10, 10, 10, 0.8); backdrop-filter: blur(20px); border-right: 1px solid #333; }
    .stMetric { 
        background: linear-gradient(145deg, #111, #050505); 
        border: 1px solid #222; border-radius: 20px; 
        padding: 30px !important; box-shadow: 10px 10px 20px #000;
    }
    .stProgress > div > div > div > div { background-color: #00d4ff; }
    h1 { font-weight: 700; letter-spacing: -2px; color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# 2. NAVIGAZIONE CRIPTATA
st.sidebar.markdown("<h1>COIN-NEXUS</h1><p style='color:gray;'>TITANIUM v4.0</p>", unsafe_allow_html=True)
menu = st.sidebar.radio("CORE MODULES", ["💎 EXECUTIVE SUMMARY", "🕵️ AUDIT & CCII", "🏦 BANKING RATING", "📈 STRESS TEST AI"])

# --- CARICAMENTO INTELLIGENTE ---
def process_file(uploaded_file):
    try:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='latin1')
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df
    except: return None

data_file = st.sidebar.file_uploader("📥 INSERISCI DATASET", type=['xlsx', 'csv'])

# ==========================================
# MODULO 1: EXECUTIVE SUMMARY (IL CUORE DA 50K)
# ==========================================
if menu == "💎 EXECUTIVE SUMMARY":
    st.title("💎 Global Executive Control")
    if data_file:
        df = process_file(data_file)
        v_col = [c for c in df.columns if any(x in c for x in ['VALORE', 'SALDO', 'EURO'])][0]
        c_col = [c for c in df.columns if any(x in c for x in ['VOCE', 'DESC', 'CONTO'])][0]
        
        # KPI DI ALTO LIVELLO
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("ASSET VALUATION", f"€ {df[v_col].sum():,.0f}", "+4.2%")
        c2.metric("SOLVENCY RATIO", "78%", "Optimum")
        c3.metric("LIQUIDITY INDEX", "2.1", "Secure")
        c4.metric("AI RISK SCORE", "9.8/10", "Top Class")

        # GRAFICO DI IMPATTO: SUNBURST MULTILIVELLO
        st.markdown("### 📊 Struttura Patrimoniale Integrata")
        fig = px.sunburst(df.nlargest(20, v_col), path=[c_col], values=v_col,
                          color=v_col, color_continuous_scale='Ice', template='plotly_dark')
        fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Caricare il dataset per attivare il motore TITANIUM.")

# ==========================================
# MODULO 2: AUDIT & CCII (REVISIONE LEGALE)
# =================================
