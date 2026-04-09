import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 1. SETUP HIGH-END
st.set_page_config(page_title="COIN-NEXUS TITANIUM", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&display=swap');
    .main { background: radial-gradient(circle at 50% 50%, #020617, #000000); color: #f1f5f9; font-family: 'Space Grotesk', sans-serif; }
    [data-testid="stSidebar"] { background: rgba(15, 23, 42, 0.9); backdrop-filter: blur(20px); border-right: 1px solid #00d4ff; }
    .stMetric { background: rgba(30, 41, 59, 0.7); border: 1px solid #00d4ff; border-radius: 15px; padding: 20px; box-shadow: 0 0 20px rgba(0, 212, 255, 0.2); }
    h1 { text-shadow: 0 0 15px #00d4ff; color: #ffffff; letter-spacing: -1px; }
    .status-tag { padding: 5px 15px; border-radius: 20px; background: #00d4ff; color: #000; font-weight: bold; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR - DEFINIZIONE MENU (CORREZIONE NAMEERROR)
st.sidebar.title("⚡ NEBULA-X CORE")

# DEFINISCI QUI TUTTE LE VOCI DEL MENU
menu_options = [
    "💎 RIEPILOGO ESECUTIVO", 
    "🕵️ RISCHIO REVISIONE (BIG4)", 
    "🛡️ SCUDO DI RISCHIO", 
    "📈 PROIEZIONI FLUSSI"
]

menu = st.sidebar.radio("MODULI OPERATIVI", menu_options)

uploaded_file = st.sidebar.file_uploader("📥 CARICA BILANCIO (XLSX/CSV)", type=['xlsx', 'csv'])

# --- LOGICA DATI ---
if uploaded_file:
    try:
        if uploaded_file.name.endswith('.xlsx'): df = pd.read_excel(uploaded_file)
        else: df = pd.read_csv(uploaded_file, sep=None, engine='python')
        df.columns = [str(c).upper() for c in df.columns]
        demo_mode = False
    except: demo_mode = True
else:
    df = pd.DataFrame({'VOCE': ['Liquidità', 'Crediti', 'Debiti'], 'VALORE': [500, 300, 200]})
    demo_mode = True

# ==========================================
# MODULO 1: RIEPILOGO ESECUTIVO
# ==========================================
if menu == "💎 RIEPILOGO ESECUTIVO":
    st.markdown(f"<h1>💎 Riepilogo Esecutivo {'<span class="status-tag">DEMO</span>' if demo_mode else ''}</h1>", unsafe_allow_html=True)
    v_col = 'VALORE' if 'VALORE' in df.columns else df.columns[1]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("TOTALE ATTIVO", f"€ {df[v_col].sum():,.0f}", "+3.2%")
    c2.metric("SALUTE AZIENDALE", "94/100", "ECCELLENTE")
    c3.metric("LIVELLO RISCHIO", "BASSO", "-5%", delta_color="inverse")

    st.subheader("📊 Mappa Patrimoniale (Sunburst)")
    fig = px.sunburst(df, path=[df.columns[0]], values=v_col, color=v_col, color_continuous_scale='GnBu', template='plotly_dark')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=0, l=0, r=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# MODULO 2: RISCHIO REVISIONE (MODELLO BIG4)
# ==========================================
elif menu == "🕵️ RISCHIO REVISIONE (BIG4)":
    st.title("🕵️ Valutazione Rischio Professionale")
    st.caption("Modello di calcolo basato su standard ISA (International Standards on Auditing)")
    
    col_input, col_viz = st.columns([1, 1])
    
    with col_input:
        ir = st.select_slider("Rischio Intrinseco (Inherent Risk)", options=[0.1, 0.3, 0.5, 0.8, 1.0], value=0.5)
        cr = st.select_slider("Rischio di Controllo (Control Risk)", options=[0.1, 0.3, 0.5,
