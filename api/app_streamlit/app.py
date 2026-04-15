# app_streamlit/app.py
import streamlit as st
from engine.scoring import calculate_metrics
from services.decision import get_credit_approval

# UI per mostrare al cliente come lavora l'API
st.title("🏛️ Coin-Nexus | Decision Engine Demo")

with st.sidebar:
    st.header("⚙️ API Configuration")
    st.info("Connected to local Credit Engine v1.0")

# Form di input...
# (Codice UI precedente aggiornato per importare da ..services.decision)
