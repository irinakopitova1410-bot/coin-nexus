import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. Configurazione (Deve essere la prima istruzione Streamlit)
st.set_page_config(page_title="Coin-Nexus", layout="wide")

# 2. Fix Path (Tutto a sinistra, zero spazi)
base_path = os.path.dirname(os.path.abspath(__file__))
if base_path not in sys.path:
    sys.path.insert(0, base_path)

# 3. Import Moduli
from engine.scoring import calculate_metrics
from services.decision import get_credit_approval
from utils.parser import extract_financials

# --- INTERFACCIA SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/bank.png", width=80)
    st.title("Nexus Control Panel")
    st.divider()
    upload_mode = st.radio("Metodo:", ["Manuale", "Upload ERP"])

    input_data = {"revenue": 1000000, "ebitda": 200000, "debt": 400000, "short_debt": 150000}
    
    if upload_mode == "Upload ERP":
        file = st.file_uploader("Carica file", type=["xlsx", "csv"])
        if file:
            try:
                df = pd.read_excel(file) if "xlsx" in file.name else pd.read_csv(file)
                parsed = extract_financials(df)
                input_data.update(parsed)
                st.success("Dati caricati!")
            except:
                st.error("Errore caricamento")

    st.subheader("Parametri Finanziari")
    name = st.text_input("Ragione Sociale", "Azienda Target S.p.A.")
    rev = st.number_input("Ricavi (€)", value=int(input_data["revenue"]))
    ebit = st.number_input("EBITDA (€)", value=int(input_data["ebitda"]))
    d_tot = st.number_input("Debito Totale (€)", value=int(input_data["debt"]))
    d_short = st.number_input("Breve Termine (€)", value=int(input_data["short_debt"]))

# --- LOGICA DI CALCOLO E DASHBOARD ---
st.title("🏛️ Coin-Nexus | Decision Intelligence")
st.caption(f"Analisi per: {name}")

if st.button("ESEGUI AUDIT BANCARIO", type="primary", use_container_width=True):
    metrics = calculate_metrics({"revenue": rev, "ebitda": ebit, "debt": d_tot, "short_debt": d_short})
    res = get_credit_approval(metrics)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("RATING", res['rating'])
        st.subheader(f"Esito: {res['decision']}")
    
    with col2:
        st.metric("SCORE", f"{res['score']}/100")
        st.write("Capacità Credito:")
        st.title(f"€ {res.get('estimated_credit', 0):,}")
    
    with col3:
        fig = go.Figure(go.Indicator(
            mode="gauge+number", 
            value=metrics.get('dscr', 0),
            gauge={'axis': {'range': [0, 5]}, 'bar': {'color': res['color']}}
        ))
        st.plotly_chart(fig, use_container_width=True)

    t1, t2 = st.tabs(["Dettagli", "Strategia"])
    with t1:
        st.write(f"Margin: {metrics.get('margin', 0)}% | Leverage: {metrics.get('leverage', 0)}")
        if res.get('issues'):
            for i in res['issues']: 
                st.warning(i)
    with t2:
        if res.get('suggestions'):
            for s in res['suggestions']: 
                st.info(s)
        else:
            st.write("Nessun suggerimento particolare al momento.")

# L'istruzione ELSE deve essere allineata esattamente all'istruzione IF del pulsante iniziale
else:
    st.info("Configura i dati nella sidebar e clicca su 'Esegui Audit' per iniziare l'analisi.")
