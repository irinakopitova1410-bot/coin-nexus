import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. Configurazione pagina
st.set_page_config(page_title="Coin-Nexus Enterprise", layout="wide", page_icon="🏛️")

# 2. Fix per i percorsi dei moduli
base_path = os.path.dirname(os.path.abspath(__file__))
if base_path not in sys.path:
    sys.path.insert(0, base_path)

# 3. Import moduli
from engine.scoring import calculate_metrics
from services.decision import get_credit_approval
from utils.parser import extract_financials

# --- INTERFACCIA SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/bank.png", width=80)
    st.title("Nexus Control Panel")
    st.divider()
    upload_mode = st.radio("Metodo Inserimento:", ["Manuale", "Upload ERP (Excel/CSV)"])

    input_data = {
        "revenue": 1000000, 
        "ebitda": 200000, 
        "debt": 400000, 
        "short_debt": 150000
    }
    
    if upload_mode == "Upload ERP (Excel/CSV)":
        file = st.file_uploader("Carica Bilancio/Export", type=["xlsx", "csv"])
        if file:
            try:
                df = pd.read_excel(file) if "xlsx" in file.name else pd.read_csv(file)
                parsed = extract_financials(df)
                st.success("✅ Dati ERP estratti!")
                input_data.update(parsed)
            except Exception as e:
                st.error(f"Errore parser: {e}")

    st.subheader("Parametri Finanziari")
    name = st.text_input("Ragione Sociale", "Azienda Target S.p.A.")
    rev = st.number_input("Ricavi (€)", value=int(input_data["revenue"]))
    ebit = st.number_input("EBITDA (€)", value=int(input_data["ebitda"]))
    d_tot = st.number_input("Debito Totale (€)", value=int(input_data["debt"]))
    d_short = st.number_input("di cui Breve Termine (€)", value=int(input_data["short_debt"]))

# --- LOGICA DI CALCOLO E DASHBOARD ---
st.title("🏛️ Coin-Nexus | Decision Intelligence")
st.caption(f"Analisi Creditizia in tempo reale per: **{name}**")

# Inizio blocco logico principale
if st.button("ESEGUI AUDIT BANCARIO", type="primary", use_container_width=True):
    metrics = calculate_metrics({
        "revenue": rev, 
        "ebitda": ebit, 
        "debt": d_tot, 
        "short_debt": d_short
    })
    
    res = get_credit_approval(metrics)
    st.divider()
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.metric("RATING", res['rating'])
        st.subheader(f"Esito: :{res['color'][1:]}[{res['decision']}]")
    
    with col2:
        st.metric("SCORE", f"{res['score']}/100")
        st.write("**Capacità di Credito Stimata:**")
        st.title(f"€ {res.get('estimated_credit', 0):,}")

    with col3:
        fig = go.Figure(go.Indicator(
            mode="gauge+number", 
            value=metrics.get('dscr', 0),
            title={'text': "Indice DSCR"},
            gauge={'axis': {'range': [0, 5]}, 'bar': {'color': res['color']}}
        ))
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)

    tab1, tab2 = st.tabs(["📊 Analisi Dettagliata", "💡 Strateg
