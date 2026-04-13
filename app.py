import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime
from sklearn.ensemble import IsolationForest

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="COIN-NEXUS QUANTUM AI", layout="wide", page_icon="💠")

# --- 2. SISTEMA DI ACCESSO ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if st.session_state["authenticated"]:
        return True

    st.markdown("<h1 style='text-align: center; color: #00f2ff;'>💠 COIN-NEXUS ACCESS</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='background: rgba(10,20,40,0.8); padding:20px; border-radius:10px; border:1px solid #00f2ff'>", unsafe_allow_html=True)
        st.write("Inserisci la chiave di licenza Platinum per accedere.")
        pwd = st.text_input("CHIAVE DI ACCESSO", type="password")
        if st.button("SBLOCCA SISTEMA"):
            if pwd == "PLATINUM2026":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Chiave non valida.")
        st.markdown("</div>", unsafe_allow_html=True)
    return False

if not check_password():
    st.stop()

# --- 3. MOTORE DI RATING E SOLVIBILITÀ (INNOVAZIONE) ---
def analizza_solvibilita(df, col_val):
    totale_ricavi = df[col_val].sum()
    # Simulazione costi operativi (70%) e margine
    ebitda_stimato = totale_ricavi * 0.30 
    
    if ebitda_stimato > 500000: # Esempio di soglia per Classe A
        return "ALTA SOLVIBILITÀ (Rating A)", "🟢", "L'azienda presenta flussi solidi e capacità di rimborso eccellente."
    elif ebitda_stimato > 100000:
        return "SOLVIBILE (Rating B)", "🟡", "Equilibrio finanziario mantenuto. Monitorare i flussi di cassa."
    else:
        return "RISCHIO SOLVIBILITÀ (Rating C)", "🔴", "Attenzione: Margini ridotti. Rischio di tensione finanziaria elevato."

# --- 4. FUNZIONI TECNICHE ---
def detect_ai_anomalies(df, col_val):
    X = df[[col_val]].values
    model = IsolationForest(contamination=0.05, random_state=42)
    df['ai_risk_score'] = model.fit_predict(X)
    return df[df['ai_risk_score'] == -1].copy()

def genera_pdf_platinum(massa, mat, ai_anom, rating, studio, note):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(0, 10, 31)
        pdf.rect(0, 0, 210, 50, 'F')
        pdf.set_text_color(0, 242, 255)
        pdf.set_font("Arial", 'B', 24)
        pdf.cell(190, 30, str(studio).upper(), ln=True, align='C')
        pdf.set_text_color(0, 0, 0)
        pdf.ln(30)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"REPORT DI VALUTAZIONE BANCARIA - RATING: {rating}", ln=True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(100, 10, "Massa Ricavi Analizzata:", 1); pdf.cell(90, 10, f"{massa:,.2f}", 1, 1, 'R')
        pdf.cell(10
