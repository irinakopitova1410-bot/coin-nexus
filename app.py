import streamlit as st
import plotly.graph_objects as go
from scoring import NexusScorer

st.set_page_config(page_title="Coin-Nexus Terminal", layout="wide")

# Sidebar Input
with st.sidebar:
    st.header("📊 ERP Data Input")
    company = st.text_input("Azienda", "Azienda Target S.r.l.")
    rev = st.number_input("Ricavi (€)", value=5450000)
    costs = st.number_input("Costi (€)", value=4500000)
    debt = st.number_input("Debito (€)", value=1200000)
    run = st.button("🚀 ESEGUI AUDIT BANCARIO")

st.title("🏛️ Coin-Nexus | Enterprise Risk Terminal")

if run:
    scorer = NexusScorer(rev, costs, debt)
    mat = scorer.calculate_isa_320()
    bep, safety = scorer.calculate_bep()
    rating, desc = scorer.get_nexus_rating()

    # KPI Principali
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rating Basel IV", rating, desc)
    c2.metric("Soglia ISA 320", f"€{mat:,.0f}")
    c3.metric("Break-Even Point", f"€{bep:,.0f}")
    c4.metric("Margine Sicurezza", f"{safety}%")

    # Grafico Radar
    st.subheader("🎯 Analisi Comparativa Asset")
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[90, 85, 80, 75, 95], theta=['Solvibilità', 'Redditività', 'Liquidità', 'Efficienza', 'Resilienza'],
        fill='toself', name='Azienda', line_color='cyan'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    st.success(f"✅ Protocollo 'Telepass Bancario' attivato per {company}")
else:
    st.info("👈 Inserisci i dati e clicca 'Esegui Audit' per generare il report.")
