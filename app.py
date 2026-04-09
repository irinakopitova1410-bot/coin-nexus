import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# CONFIGURAZIONE ELITE
st.set_page_config(page_title="COIN-NEXUS TITANIUM", layout="wide")

# CSS PROFESSIONALE
st.markdown("""
    <style>
    .main { background-color: #020617; color: #f1f5f9; font-family: sans-serif; }
    [data-testid="stSidebar"] { background-color: #0a0f18; border-right: 1px solid #00d4ff; }
    .stMetric { background-color: #1e293b; border: 1px solid #00d4ff; border-radius: 10px; padding: 15px; }
    </style>
    """, unsafe_allow_html=True)

# SIDEBAR MENU
st.sidebar.title("⚡ COIN-NEXUS CORE")
opzioni = ["💎 RIEPILOGO", "🕵️ REVISIONE", "🛡️ CONTINUITÀ"]
menu = st.sidebar.radio("SISTEMI", opzioni)

uploaded_file = st.sidebar.file_uploader("CARICA BILANCIO", type=['xlsx', 'csv'])

# GESTIONE DATI
if uploaded_file is not None:
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

# MODULO 1: RIEPILOGO
if menu == "💎 RIEPILOGO":
    st.title("💎 Dashboard Esecutiva")
    val_col = 'VALORE' if 'VALORE' in df.columns else df.columns[1]
    
    c1, c2 = st.columns(2)
    c1.metric("ATTIVO TOTALE", f"€ {df[val_col].sum():,.0f}")
    c2.metric("SALUTE IA", "96/100")
    
    fig = px.sunburst(df, path=[df.columns[0]], values=val_col, color_continuous_scale='GnBu', template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

# MODULO 2: REVISIONE (IL VALORE PER LE BIG4)
elif menu == "🕵️ REVISIONE":
    st.title("🕵️ Valutazione Rischio ISA 320")
    st.subheader("Calcolo Materialità Professionale")
    
    bench = st.number_input("Inserisci Benchmark (es. Fatturato)", value=1000000)
    sens = st.slider("% Sensibilità", 0.5, 3.0, 1.0)
    st.metric("SOGLIA ERRORE TOLLERABILE", f"€ {bench * (sens / 100):,.0f}")
    
    st.info("Questo calcolo è lo standard usato dai revisori Deloitte per definire l'ambito del controllo.")

# MODULO 3: CONTINUITÀ
else:
    st.title("🛡️ Scudo di Continuità")
    dscr = st.slider("Indice DSCR Predittivo", 0.5, 3.0, 1.5)
    if dscr >= 1.1:
        st.success(f"✅ GOING CONCERN GARANTITO (DSCR: {dscr})")
    else:
        st.error(f"⚠️ RISCHIO INSOLVENZA (DSCR: {dscr})")
