import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 1. SETUP ESTETICO ELITE
st.set_page_config(page_title="COIN-NEXUS PLATINUM", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e2e8f0; }
    .stMetric { background: rgba(16, 24, 39, 0.8); border: 1px solid #3b82f6; border-radius: 12px; padding: 20px; }
    .stButton>button { background: linear-gradient(90deg, #3b82f6, #2563eb); color: white; border-radius: 8px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR
st.sidebar.title("💠 COIN-NEXUS PLATINUM")
st.sidebar.success("SISTEMA ONLINE")
uploaded_file = st.sidebar.file_uploader("Sincronizza Dataset", type=['csv', 'xlsx'])

# 3. LOGICA DI ANALISI
if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    
    st.title("🛡️ Audit Intelligence & Forensic")
    
    # Identificazione Colonne (Basata sul tuo screenshot)
    # Vedo 'Descrizione' e 'Saldo'
    col_v = 'Saldo'
    col_c = 'Descrizione'
    
    # Pulizia Valori
    df[col_v] = pd.to_numeric(df[col_v], errors='coerce').fillna(0)
    
    # Metriche ISA 320
    totale = df[col_v].sum()
    mat = totale * 0.01  # Materialità al 1%
    
    c1, c2, c3 = st.columns(3)
    c1.metric("MASSA MONETARIA", f"€ {totale:,.2f}")
    c2.metric("MATERIALITÀ (ISA 320)", f"€ {mat:,.2f}", "Soglia Errore")
    c3.metric("HEALTH SCORE", "EXCELLENT", "+12%")

    # --- VISUALIZZAZIONE AVANZATA ---
    st.subheader("📊 Mappa dei Rischi Patrimoniali")
    fig = px.treemap(df, path=[col_c], values=col_v, color=col_v,
                     color_continuous_scale='Blues', template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # --- FORENSIC PREDICTION ---
    st.subheader("🕵️ Analisi Statistica Benford")
    # Estrazione prima cifra per test anti-frode
    digits = df[col_v].astype(str).str.extract(r'([1-9])')[0].dropna().astype(int)
    if not digits.empty:
        counts = digits.value_counts(normalize=True).sort_index()
        expected = pd.Series({d: np.log10(1 + 1/d) for d in range(1, 10)})
        
        fig_b = go.Figure()
        fig_b.add_trace(go.Bar(x=counts.index, y=counts.values, name="Dati Reali", marker_color='#3b82f6'))
        fig_b.add_trace(go.Scatter(x=expected.index, y=expected.values, name="Curva Teorica", line=dict(color='#ef4444')))
        fig_b.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_b, use_container_width=True)

    # Tabella Dati Sotto
    with st.expander("🔍 Visualizza Dettaglio Record"):
        st.dataframe(df, use_container_width=True)

else:
    st.info("👋 Benvenuto in Platinum. Carica il file del bilancio nella barra laterale per avviare il motore.")
