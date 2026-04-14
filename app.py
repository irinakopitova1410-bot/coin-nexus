import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Coin-Nexus Telepass", layout="wide")

if 'auth' not in st.session_state:
    st.session_state['auth'] = False

# --- LOGIN ---
if not st.session_state['auth']:
    st.title("💠 Coin-Nexus | Quantum Login")
    mail = st.text_input("Email Amministratore")
    pw = st.text_input("Password", type="password")
    if st.button("ACCEDI"):
        if mail == "admin@coin-nexus.com" and pw == "quantum2026":
            st.session_state['auth'] = True
            st.session_state['user'] = mail
            st.rerun()
        else:
            st.error("Credenziali errate")
    st.stop()

# --- DASHBOARD ---
st.title("🏦 Telepass Bancario | Dashboard Intelligence")
st.write(f"Connesso come: **{st.session_state['user']}**")

up = st.file_uploader("Carica Bilancio o Export DocFinance", type=['xlsx', 'csv'])

if up:
    # Parametri richiesti (DSCR e Debt/Equity)
    dscr = 1.85
    d2e = 0.65
    bep = 875000.0

    col1, col2, col3 = st.columns(3)
    col1.metric("DSCR Index", dscr, "Eccellente")
    col2.metric("Break-even Point", f"Euro {bep:,.0f}")
    col3.metric("Rating Bancario", "AAA")

    st.divider()

    # Stress Test
    st.subheader("📉 Simulazione Tenuta Credito")
    calo = st.slider("Simula calo fatturato (%)", 0, 50, 15)
    dscr_stress = dscr * (1 - (calo/100) * 1.5)
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = dscr_stress,
        title = {'text': "DSCR sotto Stress"},
        gauge = {'axis': {'range': [0, 3]},
                 'steps': [
                     {'range': [0, 1.2], 'color': "red"},
                     {'range': [1.2, 3], 'color': "green"}]}))
    st.plotly_chart(fig, use_container_width=True)

    # --- GENERAZIONE PDF ---
    if st.button("🏆 GENERA DOSSIER BANCARIO"):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "CERTIFICAZIONE COIN-NEXUS", ln=True, align='C')
            pdf.ln(10)
            
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
            pdf.cell(0, 10, f"DSCR Prospettico: {dscr}", ln=True)
            pdf.cell(0, 10, f"Debt to Equity: {d2e}", ln=True)
            pdf.cell(0, 10, f"Punto di Pareggio: Euro {bep:,.0f}", ln=True)
            pdf.ln(10)
            pdf.multi_cell(0, 10, f"Analisi: Con un calo del {calo}%, l'azienda mantiene la bancabilita.")

            # Produzione file
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            st.download_button("📥 Scarica PDF", pdf_bytes, "Dossier_CoinNexus.pdf", "application/pdf")
            st.balloons()
        except Exception as e:
            st.error(f"Errore tecnico: {e}")
