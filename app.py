import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from engine.scoring import calculate_metrics
from services.decision import get_credit_approval
from utils.parser import extract_financials # Assicurati di averlo in utils/parser.py

st.set_page_config(page_title="Coin-Nexus Enterprise", layout="wide")

st.title("🏛️ Coin-Nexus | Decision Intelligence")

# --- SIDEBAR: INPUT DATI ---
with st.sidebar:
    st.header("📥 Input Dati")
    upload_mode = st.radio("Metodo inserimento:", ["Manuale", "Upload ERP (Excel/CSV)"])
    
    # Valori di default
    extracted_data = {"revenue": 1000000, "ebitda": 200000, "debt": 400000, "short_debt": 100000}
    
    if upload_mode == "Upload ERP (Excel/CSV)":
        file = st.file_uploader("Carica export gestionale", type=["xlsx", "csv"])
        if file:
            df = pd.read_excel(file) if "xlsx" in file.name else pd.read_csv(file)
            parsed = extract_financials(df)
            st.success(f"Dati estratti! Qualità: {parsed['data_quality'].upper()}")
            # Aggiorniamo i valori di default con quelli estratti dal parser
            extracted_data.update(parsed)

    # Campi di input (pre-compilati se c'è l'upload)
    name = st.text_input("Ragione Sociale", "Target S.p.A.")
    rev = st.number_input("Ricavi (€)", value=int(extracted_data.get("revenue", 1000000)))
    ebit = st.number_input("EBITDA (€)", value=int(extracted_data.get("ebitda", 200000)))
    debt_tot = st.number_input("Debito Totale (€)", value=int(extracted_data.get("debt", 400000)))
    debt_short = st.number_input("Debito Breve Termine (€)", value=int(extracted_data.get("short_debt", 100000)))

# --- LOGICA CORE ---
if st.button("ESEGUI AUDIT BANCARIO"):
    # 1. Calcolo metriche (Engine)
    m = calculate_metrics({
        "revenue": rev, "ebitda": ebit, 
        "debt": debt_tot, "short_debt": debt_short
    })
    
    # 2. Ottenimento decisione (Service)
    d = get_credit_approval(m)
    
    # --- VISUALIZZAZIONE RISULTATI ---
    st.divider()
    c1, c2, c3 = st.columns([1, 1, 1])
    
    with c1:
        st.metric("RATING", d['rating'])
        st.subheader(f"Esito: :{d['color'][1:]}[{d['decision']}]")
    
    with c2:
        st.metric("SCORE", f"{d['score']}/100")
        st.write(f"**Credito Stimato:** € {d['estimated_credit']:,}")

    with c3:
        # Gauge Chart per il DSCR
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=m['dscr'],
            title={'text': "Indice DSCR"},
            gauge={'axis': {'range': [0, 5]}, 'bar': {'color': d['color']}}
        ))
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # --- SUGGERIMENTI E CRITICITÀ ---
    col_a, col_b = st.columns(2)
    with col_a:
        st.warning("⚠️ **Criticità Rilevate**")
        for issue in d['issues']:
            st.write(f"- {issue}")
            
    with col_b:
        st.info("💡 **Suggerimenti per il Miglioramento**")
        for sug in d['suggestions']:
            st.write(f"- {sug}")

    # --- SIMULAZIONE ---
    st.success(f"🚀 **Potenziale Rating:** Riducendo il debito a breve, il tuo score salirebbe a **{d['simulation']['improved_score']}**")
