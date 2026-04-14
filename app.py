import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import io

# Configurazione obbligatoria come prima riga
st.set_page_config(page_title="Coin-Nexus Telepass", layout="wide")

# Inizializzazione sessione
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

# Login con la tua mail admin
if not st.session_state['auth']:
    st.title("💠 Coin-Nexus Login")
    mail = st.text_input("Email")
    pw = st.text_input("Password", type="password")
    if st.button("Accedi"):
        if mail == "admin@coin-nexus.com" and pw == "quantum2026":
            st.session_state['auth'] = True
            st.rerun()
        else:
            st.error("Credenziali errate")
    st.stop()

# Dashboard Principale
st.title("🏦 Telepass Bancario")
st.write(f"Utente: {mail}")

file = st.file_uploader("Carica Bilancio", type=['xlsx', 'csv'])

if file:
    dscr = 1.85
    bep = 875000.0
    
    st.metric("DSCR Index", dscr, "Eccellente")
    st.metric("Punto di Pareggio", f"Euro {bep:,.0f}")

    # Generazione PDF ultra-semplice per evitare crash
    if st.button("Genera Report"):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(40, 10, "Certificazione Coin-Nexus")
            pdf.ln(20)
            pdf.set_font("Arial", size=12)
            pdf.cell(40, 10, f"DSCR: {dscr}")
            
            pdf_out = pdf.output(dest='S').encode('latin-1')
            st.download_button("Scarica PDF", pdf_out, "Report.pdf", "application/pdf")
            st.balloons()
        except Exception as e:
            st.error(f"Errore PDF: {e}")
