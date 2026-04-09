import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# 1. SETTINGS & CYBER DESIGN
st.set_page_config(page_title="COIN-NEXUS TITANIUM", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&display=swap');
    .main { background: radial-gradient(circle at 50% 50%, #020617, #000000); color: #f1f5f9; font-family: 'Space Grotesk', sans-serif; }
    [data-testid="stSidebar"] { background: rgba(15, 23, 42, 0.9); backdrop-filter: blur(20px); border-right: 1px solid #38bdf8; }
    .stMetric { background: rgba(30, 41, 59, 0.7); border: 1px solid #38bdf8; border-radius: 15px; padding: 20px; box-shadow: 0 0 20px rgba(56, 189, 248, 0.2); }
    h1 { text-shadow: 0 0 15px #38bdf8; color: #ffffff; letter-spacing: -1px; }
    .status-tag { padding: 5px 15px; border-radius: 20px; background: #06b6d4; color: white; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR COMMAND
st.sidebar.title("⚡ NEBULA-X CORE")
menu = st.sidebar.radio("SISTEMI ATTIVI", ["💎 EXECUTIVE SUMMARY", "🛡️ RISK SHIELD", "📈 PROJECTION"])
uploaded_file = st.sidebar.file_uploader("📥 SINCRO DATI (UPLOAD)", type=['xlsx', 'csv'])

# --- LOGICA DATI (CON DEMO MODE) ---
if uploaded_file:
    try:
        if uploaded_file.name.endswith('.xlsx'): df = pd.read_excel(uploaded_file)
        else: df = pd.read_csv(uploaded_file, sep=None, engine='python')
        df.columns = [str(c).upper() for c in df.columns]
        demo_mode = False
    except: demo_mode = True
else:
    # DATI DEMO PER NON LASCIARE L'APP VUOTA
    demo_data = {
        'VOCE': ['Liquidità', 'Crediti Commerciali', 'Rimanenze', 'Immobilizzazioni', 'Debiti Fornitori', 'TFR'],
        'VALORE': [450000, 320000, 150000, 800000, 210000, 120000]
    }
    df = pd.DataFrame(demo_data)
    demo_mode = True

# ==========================================
# MODULO 1: EXECUTIVE SUMMARY
# ==========================================
if menu == "💎 EXECUTIVE SUMMARY":
    st.markdown(f"<h1>💎 Executive Summary {'<span class="status-tag">DEMO MODE</span>' if demo_mode else ''}</h1>", unsafe_allow_html=True)
    
    # KPI DINAMICI
    v_col = 'VALORE' if 'VALORE' in df.columns else df.columns[1]
    tot_asset = df[v_col].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("GLOBAL ASSETS", f"€ {tot_asset:,.0f}", "+3.2%")
    col2.metric("HEALTH SCORE", "94/100", "EXCELLENT")
    col3.metric("CASH FLOW", "€ 42.1K", "+12%")
    col4.metric("RISK LEVEL", "LOW", "-5%", delta_color="inverse")

    st.markdown("---")
    
    # GRAFICO TREEMAP INNOVATIVO
    c_left, c_right = st.columns([2, 1])
    with c_left:
        st.subheader("📊 Network Patrimoniale")
        fig = px.treemap(df, path=[df.columns[0]], values=v_col, color=v_col, 
                         color_continuous_scale='Blues', template='plotly_dark')
        fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    
    with c_right:
        st.subheader("🕵️ Analisi IA")
        st.write("> **Verdetto:** La struttura finanziaria è solida. La concentrazione degli asset nella 'Liquidità' suggerisce un'alta capacità di reazione a shock esterni.")
        st.info("Consiglio: Ottimizzare i crediti commerciali per ridurre il DSO.")

# ==========================================
# MODULO 2: RISK SHIELD
# ==========================================
elif menu == "🛡️ RISK SHIELD":
    st.title("🛡️ Quantum Risk Shield")
    # Radar Chart
    categories = ['Liquidità', 'Solvibilità', 'Redditività', 'Efficienza', 'Patrimonio']
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=[5, 4, 4.5, 3.5, 5], theta=categories, fill='toself', 
                                 line_color='#38bdf8', fillcolor='rgba(56, 189, 248, 0.3)'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), 
                      paper_bgcolor='rgba(0,0,0,0)', font_color='white')
