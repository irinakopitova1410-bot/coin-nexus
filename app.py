import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

# CONFIGURAZIONE MINIMA
st.set_page_config(page_title="COIN-NEXUS TEST", page_icon="💠")

if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    pwd = st.text_input("Inserisci Password", type="password")
    if st.button("Entra"):
        if pwd == "PLATINUM2026":
            st.session_state["auth"] = True
            st.rerun()
        else:
            st.error("Sbagliata")
    st.stop()

st.title("💠 COIN-NEXUS ONLINE")
uploaded = st.file_uploader("Carica file", type=['csv', 'xlsx'])

if uploaded:
    df = pd.read_excel(uploaded) if uploaded.name.endswith('.xlsx') else pd.read_csv(uploaded)
    st.success("File caricato con successo!")
    st.write(df.head())
