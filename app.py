import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. Configurazione Pagina
st.set_page_config(page_title="Coin-Nexus | Advanced Audit", layout="wide", page_icon="🏛️")

# 2. Fix Path
base_path = os.path.dirname(os.path.abspath(__file__))
if base_path not in sys.path:
    sys.path.insert(0, base_path)

from engine.scoring import calculate_metrics
from services.decision import get_credit_approval
from utils.parser import extract_financials

# --- FUNZIONE LOGICA AUDIT AVANZATO ---
def get_advanced_audit(metrics, isa_score):
    rev = metrics.get('revenue', 0)
    materiality = rev * 0.015  # Standard ISA 320 al 1.5%
    trivial_error = materiality * 0.05
    
    # Valutazione Solidità 4 Anni (Forward Looking)
    dscr = metrics.get('dscr', 0)
    if dscr > 1.4 and isa_score >= 8:
        solidity = "ECCELLENTE"
        color = "#00CC66"
    elif dscr >= 1.1:
        solidity = "STABILE"
        color = "#FFCC00"
    else:
        solidity = "VULNERABILE"
        color = "#FF3300"
        
    return {
        "materiality": materiality,
        "trivial_error": trivial_error,
        "solidity_4y": solidity,
        "color": color,
        "opinion": "SENZA RILIEVI" if dscr > 1.1 else "CON RILIEVI"
    }

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/business-network.png", width=80)
    st.title("Quantum Control")
    st.divider()
    
    isa_val = st.slider("Punteggio ISA (Affidabilità)", 1, 10, 8)
    st.divider()
    
    # Input Dati
    rev = st.number_input("Ricavi Totali (€)", value=1200000)
    ebit = st.number_input("EBITDA (€)", value=250000)
    d_tot = st.number_input("Debito Totale (€)", value=450000)
    d_short = st.number_input("Debito Breve (€)", value=100000)

# --- DASHBOARD PRINCIPALE ---
st.title("🏛️ Coin-Nexus | Financial Intelligence Report")
st.caption("Certificazione Digitale ISA 320 & Rating Prospettico 48 Mesi")

if st.button("ESEGUI AUDIT PROFESSIONALE", type="primary", use_container_width=True):
    # Calcoli Base
    metrics = calculate_metrics({"revenue": rev, "ebitda": ebit, "debt": d_tot, "short_debt": d_short})
    res = get_credit_approval(metrics)
    audit = get_advanced_audit(metrics, isa_val)
    
    st.divider()

    # --- SEZIONE 1: RATING & SOLIDITÀ ---
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("RATING ATTUALE", res['rating'])
        st.markdown(f"**Solidità 4 Anni:** <span style='color:{audit['color']}'>{audit['solidity_4y']}</span>", unsafe_allow_html=True)
    with c2:
        st.metric("SCORE", f"{res['score']}/100")
        st.write(f"**Giudizio:** {audit['opinion']}")
    with c3:
        st.metric("CAPACITÀ CREDITO", f"€ {res.get('estimated_credit', 0):,}")

    # --- SEZIONE 2: GRAFICI DI STRESS TEST ---
    st.markdown("---")
    st.subheader("📊 Proiezioni Prospettiche e Materialità Audit")
    
    g1, g2
