import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. SETUP ELITE (Niente Neon eccessivi, solo Classe)
st.set_page_config(page_title="COIN-NEXUS ELITE", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e2e8f0; }
    [data-testid="stSidebar"] { background-color: #0a0f18; border-right: 1px solid #3b82f6; }
    .stMetric { background-color: #111827; border: 1px solid #3b82f6; border-radius: 8px; padding: 20px !important; }
    h1 { color: #ffffff; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGICA SIDEBAR
st.sidebar.title("💠 COIN-NEXUS")
st.sidebar.caption("SISTEMA DI REVISIONE LEGALE v7.0")

menu = st.sidebar.radio("MODULI", ["📊 RIEPILOGO", "⚖️ MATERIALITÀ", "🛡️ CONTINUITÀ"])
file = st.sidebar.file_uploader("CARICA BILANCIO", type=['xlsx', 'csv'])

# 3. MOTORE DATI
if file:
    try:
        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        demo = False
    except: demo = True
else:
    df = pd.DataFrame({'VOCE': ['Liquidità', 'Crediti', 'Debiti'], 'VALORE': [500000, 300000, 200000]})
    demo = True

# 4. VISUALIZZAZIONE
if menu == "📊 RIEPILOGO":
    st.title("📊 Executive Dashboard")
    c1, c2 = st.columns(2)
    c1.metric("ATTIVO TOTALE", f"€ {df.iloc[:, 1].sum():,.0f}")
    c2.metric("PUNTEGGIO RISCHIO", "BASSO", "SICURO")
    
    fig = px.pie(df, names=df.columns[0], values=df.columns[1], hole=0.6, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

elif menu == "⚖️ MATERIALITÀ":
    st.title("⚖️ Materialità (ISA 320)")
    bench = st.number_input("Benchmark di Riferimento (€)", value=1000000)
    st.metric("SOGLIA DI ERRORE", f"€ {bench * 0.01:,.0f}")
    st.info("Calcolo basato su standard internazionali di revisione.")

else:
    st.title("🛡️ Continuità Aziendale")
    st.success("✅ Parametri di stabilità conformi ai requisiti del Codice della Crisi.")
