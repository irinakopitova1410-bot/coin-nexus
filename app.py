import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime
from sklearn.ensemble import IsolationForest

# --- SISTEMA DI ACCESSO QUANTUM ---
def check_password():
    """Restituisce True se l'utente ha inserito la password corretta."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:
        return True

    # Interfaccia di Login Quantum in Italiano
    st.markdown("""
        <style>
        .login-box {
            background-color: rgba(10, 20, 40, 0.8);
            padding: 30px;
            border-radius: 15px;
            border: 1px solid #00f2ff;
            text-align: center;
        }
        .stApp { background: #02040a; }
        </style>
        """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; color: #00f2ff;'>💠 COIN-NEXUS ACCESS</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.write("Inserisci la chiave di licenza Platinum per sbloccare l'AI.")
        pwd = st.text_input("CHIAVE DI ACCESSO (AUDIT KEY)", type="password")
        if st.button("SBLOCCA SISTEMA"):
            if pwd == "PLATINUM2026": # La tua password
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Chiave non valida. Accesso negato.")
        st.markdown("</div>", unsafe_allow_html=True)
    return False

# Blocco di sicurezza: se non autenticato, ferma l'esecuzione qui
if not check_password():
    st.stop()

# --- CONFIGURAZIONE INTERFACCIA (POST-LOGIN) ---
st.set_page_config(page_title="COIN-NEXUS QUANTUM AI", layout="wide", page_icon="💠")

st.markdown("""
    <style>
    .stApp { background: #02040a; color: #e6f1ff; }
    [data-testid="stMetricValue"] { color: #00f2ff !important; text-shadow: 0 0 10px rgba(0, 242, 255, 0.4); }
    .stMetric { background: rgba
