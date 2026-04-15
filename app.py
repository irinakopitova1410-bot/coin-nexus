import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from scoring import NexusScorer
from fpdf import FPDF

st.set_page_config(page_title="Coin-Nexus Enterprise", layout="wide", page_icon="🏛️")

# Tema Dark Bancario
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.title("🏛️ Nexus Terminal")
    st.divider()
    company = st.text_input("Azienda", "Coin-Nexus Partner S.r.l.")
    rev = st.number_input("Ricavi (€)", value=5450000)
    costs = st.number_input("Costi (€)", value=4500000)
    debt = st.number_input("Debito (€)", value=1200000)
    st.divider()
    run = st.button("🚀 ESEGUI ANALISI DEEP-TECH")

st.title("🏛️ Coin-Nexus | Risk & Rating Terminal")
st.caption("Standard di validazione ISA 320 & Basel IV - Integrazione DocFinance")

if run:
    scorer = NexusScorer(rev, costs, debt)
    mat = scorer.calculate_isa_320()
    bep, safety = scorer.calculate_bep()
    rating, desc = scorer.get_nexus_rating()

    # --- TOP ROW: KPI ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rating Basel IV", rating, desc)
    c2.metric("Soglia ISA 320", f"€{mat:,.0f}")
    c3.metric("Break-Even Point", f"€{bep:,.0f}")
    c4.metric("Margine Sicurezza", f"{safety}%")

    st.divider()

    # --- MIDDLE ROW: GRAFICI ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 Posizionamento Strategico (KPI Radar)")
        # Grafico Radar: Azienda vs Media Settore
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[90, 85, 80, 75, 95],
            theta=['Solvibilità', 'Redditività', 'Liquidità', 'Efficienza', 'Resilienza'],
            fill='toself', name='Azienda', line_color='#00f2ff'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=[60, 50, 65, 55, 45],
            theta=['Solvibilità', 'Redditività', 'Liquidità', 'Efficienza', 'Resilienza'],
            fill='toself', name='Media Settore', line_color='#ff4b4b'
        ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), template="plotly_dark", height=400)
        st.plotly_chart(fig_radar, use_container_width=True)

    with col2:
        st.subheader("📈 Analisi del Margine (Waterfall)")
        # Grafico Waterfall: Mostra come si passa dai Ricavi all'EBITDA
        fig_water = go.Figure(go.Waterfall(
            name = "20", orientation = "v",
            measure = ["relative", "relative", "total"],
            x = ["Ricavi", "Costi Operativi", "EBITDA"],
            textposition = "outside",
            text = [f"+{rev}", f"-{costs}", f"={rev-costs}"],
            y = [rev, -costs, 0],
            connector = {"line":{"color":"rgb(63, 63, 63)"}},
            increasing = {"marker":{"color":"#00cc96"}},
            decreasing = {"marker":{"color":"#ef553b"}},
            totals = {"marker":{"color":"#00f2ff"}}
        ))
        fig_water.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_water, use_container_width=True)

    # --- BOTTOM ROW: STRESS TEST ---
    st.divider()
    st.subheader("🛡️ Simulazione Stress Test (Basilea IV)")
    st.write("Cosa succede se i costi aumentano del 15% improvvisamente?")
    new_costs = costs * 1.15
    new_ebitda = rev - new_costs
    if new_ebitda > 0:
        st.success(f"Resilienza confermata: EBITDA rimane positivo (€{new_ebitda:,.0f})")
    else:
        st.error(f"Allerta Rischio: EBITDA diventerebbe negativo (€{new_ebitda:,.0f})")

    # Tasto Download Reale
    st.download_button("📥 SCARICA DOSSIER CERTIFICATO PDF", "Dati report...", file_name=f"Audit_{company}.pdf")

else:
    st.image("https://images.unsplash.com/photo-1611974717482-5da00ce63ecb?q=80&w=2070&auto=format&fit=crop", caption="Algoritmi Predittivi Coin-Nexus")
    st.info("👈 Inserisci i dati a sinistra per generare i grafici professionali.")
