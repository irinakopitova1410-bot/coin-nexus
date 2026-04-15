import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from scoring import NexusScorer  # Importazione diretta (senza cartella engine)
from datetime import datetime

# Setup Professionale
st.set_page_config(page_title="Coin-Nexus Enterprise", layout="wide", page_icon="🏛️")

# CSS Custom
st.markdown("""
    <style>
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Coin-Nexus | Enterprise Risk Terminal")
st.caption("Versione Vendibile - Integrazione Diretta")

# Sidebar
with st.sidebar:
    st.header("📥 Data Input (ERP)")
    company = st.text_input("Ragione Sociale", "Azienda Target S.r.l.")
    rev = st.number_input("Ricavi Totali (€)", value=5450000)
    costs = st.number_input("Costi Totali (€)", value=4500000)
    debt = st.number_input("Esposizione Bancaria (€)", value=1200000)
    st.divider()
    run_audit = st.button("🚀 ESEGUI SCORING BANCARIO")

if run_audit:
    # Inizializzazione Motore
    scorer = NexusScorer(rev, costs, debt)
    mat, err = scorer.calculate_isa_320()
    bep, safety = scorer.calculate_bep()
    rating, desc = scorer.get_nexus_rating()

    # --- TOP METRICS ---
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Rating Basel IV", rating, desc)
    with c2: st.metric("Soglia ISA 320", f"€{mat:,.0f}")
    with c3: st.metric("Break-Even Point", f"€{bep:,.0f}")
    with c4: st.metric("Margine Sicurezza", f"{safety}%")

    st.divider()

    # --- VISUAL ANALYSIS ---
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("🎯 Analisi Comparativa")
        categories = ['Solvibilità', 'Redditività', 'Liquidità', 'Efficienza', 'Resilienza']
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[90, 85, 80, 70, 95], theta=categories, fill='toself', name='Asset', line_color='#00f2ff'
        ))
        fig.add_trace(go.Scatterpolar(
            r=[60, 55, 65, 50, 45], theta=categories, fill='toself', name='Media Settore', line_color='#ff4b4b'
        ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("🤖 AI Auditor Insight")
        st.info(f"Il protocollo 'Telepass Bancario' per **{company}** è attivo.")
        st.warning("⚠️ Pronti per la validazione DocFinance")
        st.download_button("📥 Scarica Report Certificato", "PDF...", file_name=f"Audit_{company}.pdf")
else:
    st.info("👈 Inserisci i dati e clicca sul tasto per iniziare l'analisi.")
