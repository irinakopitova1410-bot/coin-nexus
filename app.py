import streamlit as st
import plotly.graph_objects as go
from supabase import create_client
import pandas as pd

# Import dai tuoi moduli
from engine.scoring import calculate_metrics
from services.decision import get_credit_approval

st.set_page_config(page_title="Coin-Nexus", layout="wide")

# Inizializzazione Supabase con gestione errori
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception as e:
    st.error("Errore Configurazione: Inserisci le chiavi in Streamlit Secrets!")

st.title("🏛️ Coin-Nexus | Credit Decision Engine")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Dati Azienda")
    name = st.text_input("Ragione Sociale", "Target Srl")
    rev = st.number_input("Ricavi (€)", value=1000000)
    ebit = st.number_input("EBITDA (€)", value=250000)
    debt = st.number_input("Debito (€)", value=400000)
    
    if st.button("ESEGUI ANALISI"):
        m = calculate_metrics({"revenue": rev, "ebitda": ebit, "debt": debt})
        d = get_credit_approval(m)
        st.session_state['last'] = (m, d, name)

with col2:
    if 'last' in st.session_state:
        m, d, n = st.session_state['last']
        st.header(f"Rating: {d['rating']}")
        st.subheader(f"Esito: {d['decision']}")
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=m['dscr'],
            title={'text': "Indice DSCR"},
            gauge={'axis': {'range': [0, 5]}, 'bar': {'color': d['color']}}
        ))
        st.plotly_chart(fig)
