import streamlit as st
import plotly.graph_objects as go
from scoring import NexusScorer

st.set_page_config(page_title="Coin-Nexus Terminal", layout="wide", page_icon="🏛️")

# Design Enterprise
st.markdown("<style>.stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; }</style>", unsafe_allow_html=True)

with st.sidebar:
    st.title("📥 ERP Input")
    company = st.text_input("Ragione Sociale", "Azienda Prova S.p.A.")
    rev = st.number_input("Ricavi (€)", value=5450000)
    costs = st.number_input("Costi (€)", value=4500000)
    debt = st.number_input("Debito (€)", value=1200000)
    run = st.button("🚀 GENERA AUDIT")

st.title("🏛️ Coin-Nexus | Risk & Rating Terminal")
st.info("Algoritmo di validazione istantanea per l'accesso al credito (Protocollo ISA 320)")

if run:
    scorer = NexusScorer(rev, costs, debt)
    mat = scorer.calculate_isa_320()
    bep, safety = scorer.calculate_bep()
    rating, desc = scorer.get_nexus_rating()

    # KPI Row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rating Basel IV", rating, desc)
    c2.metric("Soglia ISA 320", f"€{mat:,.0f}")
    c3.metric("Break-Even Point", f"€{bep:,.0f}")
    c4.metric("Margine Sicurezza", f"{safety}%")

    # Radar Chart
    st.subheader("🎯 Posizionamento Strategico")
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[90, 85, 80, 75, 95], theta=['Solvibilità', 'Redditività', 'Liquidità', 'Efficienza', 'Resilienza'],
        fill='toself', name='Azienda', line_color='#00f2ff'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    
    st.success(f"✅ Dossier Validato. Asset '{company}' pronto per la cartolarizzazione.")
