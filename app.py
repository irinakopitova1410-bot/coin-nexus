import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Coin-Nexus | Advanced Audit", layout="wide", page_icon="🏛️")

# FIX PATH: Forza Python a trovare le cartelle locali
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from engine.scoring import calculate_metrics
    from services.decision import get_credit_approval
except ImportError as e:
    st.error(f"Errore di configurazione moduli: {e}")
    st.stop()

def get_advanced_audit(metrics, isa_score):
    rev = metrics.get('revenue', 0)
    materiality = rev * 0.015
    dscr = metrics.get('dscr', 0)
    
    if dscr > 1.4 and isa_score >= 8:
        solidity, color = "ECCELLENTE", "#00CC66"
    elif dscr >= 1.1:
        solidity, color = "STABILE", "#FFCC00"
    else:
        solidity, color = "VULNERABILE", "#FF3300"
        
    return {"materiality": materiality, "solidity_4y": solidity, "color": color}

# --- INTERFACCIA ---
with st.sidebar:
    st.header("Parametri Audit")
    isa_val = st.slider("Punteggio ISA", 1, 10, 8)
    rev_in = st.number_input("Ricavi (€)", value=1000000)
    ebit_in = st.number_input("EBITDA (€)", value=200000)
    debt_in = st.number_input("Debito Totale (€)", value=400000)
    short_in = st.number_input("Debito Breve (€)", value=100000)

st.title("🏛️ Coin-Nexus | Financial Intelligence")

if st.button("ESEGUI AUDIT PROFESSIONALE"):
    m = calculate_metrics({"revenue": rev_in, "ebitda": ebit_in, "debt": debt_in, "short_debt": short_in})
    res = get_credit_approval(m)
    audit = get_advanced_audit(m, isa_val)
    
    # KPI
    col1, col2, col3 = st.columns(3)
    col1.metric("RATING", res['rating'])
    col2.metric("SCORE", f"{res['score']}/100")
    col3.metric("SOLIDITÀ 4 ANNI", audit['solidity_4y'])

    # GRAFICO PROIEZIONE 4 ANNI
    st.subheader("📊 Sostenibilità Debito Prospettica (DSCR)")
    anni = ['Oggi', '2027', '2028', '2029', '2030']
    proiezione = [m['dscr'], m['dscr']*1.05, m['dscr']*1.1, m['dscr']*1.15, m['dscr']*1.2]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=anni, y=proiezione, mode='lines+markers', line=dict(color=audit['color'], width=4)))
    fig.add_hline(y=1.2, line_dash="dash", line_color="red")
    st.plotly_chart(fig, use_container_width=True)
    
    st.success(f"L'impresa è considerata {audit['solidity_4y']} per la concessione del credito.")
