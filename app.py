import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime
import io

# --- 1. CONFIGURAZIONE PAGINA (DEVE ESSERE LA PRIMA RIGA) ---
st.set_page_config(page_title="Coin-Nexus | Credit Pass", layout="wide", page_icon="🏦")

# --- 2. MOTORE PDF (VERSIONE COMPATIBILE) ---
class BankReport(FPDF):
    def header(self):
        self.set_fill_color(180, 0, 0) # Rosso Istituzionale
        self.rect(0, 0, 210, 45, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 25, 'DOSSIER DI CREDITO INTEGRATO - COIN-NEXUS', 0, 1, 'C')
        self.ln(20)

    def chapter(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, f" {title}", 0, 1, 'L', True)
        self.ln(4)

def genera_pdf(data):
    pdf = BankReport()
    pdf.add_page()
    
    # Sezione 1
    pdf.chapter("1. INDICATORI DI BANCABILITA (BASILEA IV)")
    pdf.set_font('Arial', '', 11)
    pdf.cell(95, 10, f"DSCR Prospettico: {data['dscr']}", 1)
    pdf.cell(95, 10, f"Debt/Equity Ratio: {data['d2e']}", 1, ln=True)
    pdf.cell(0, 10, f"Punto di Pareggio (Break-even): Euro {data['bep']:,.0f}", 1, ln=True)
    
    # Sezione 2
    pdf.ln(5)
    pdf.chapter("2. ANALISI TECNICA E STRESS TEST")
    pdf.set_font('Arial', '', 10)
    testo = data['analisi'].replace('€', 'Euro').replace('à', 'a').replace('è', 'e').replace('é', 'e').replace('ì', 'i').replace('ò', 'o').replace('ù', 'u')
    pdf.multi_cell(0, 7, testo)
    
    # Sezione 3
    pdf.ln(5)
    pdf.chapter("3. RACCOMANDAZIONI DOCFINANCE")
    for s in data['suggerimenti']:
        s_clean = s.replace('€', 'Euro').replace('à', 'a').replace('è', 'e').replace('é', 'e').replace('ì', 'i').replace('ò', 'o').replace('ù', 'u')
        pdf.multi_cell(0, 7, f"- {s_clean}")

    return pdf.output(dest='S').encode('latin-1')

# --- 3. LOGICA DI ACCESSO ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("💠 Coin-Nexus Quantum Login")
    user = st.text_input("Admin ID")
    pw = st.text_input("Password", type="password")
    if st.button("ACCEDI"):
        if user == "admin" and pw == "2026":
            st.session_state['auth'] = True
            st.rerun()
        else:
            st.error("Credenziali Errate")
    st.stop()

# --- 4. DASHBOARD ---
st.title("🏦 Telepass Bancario | Dashboard Partner")

file = st.file_uploader("Carica Dati Tesoreria / Bilancio", type=['xlsx', 'csv'])

if file:
    # Calcoli simulati (ma pronti per logica reale)
    dscr = 1.85
    d2e = 0.65
    bep = 875000.0

    col1, col2, col3 = st.columns(3)
    col1.metric("DSCR", dscr, "Target Superato")
    col2.metric("Break-even", f"€ {bep:,.0f}")
    col3.metric("Rating", "AAA")

    st.divider()
    
    # Stress Test Slider
    st.subheader("📉 Simulazione Stress Test")
    calo = st.slider("Simula calo fatturato (%)", 0, 50, 15)
    dscr_stress = dscr * (1 - (calo/100) * 1.5)
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = dscr_stress,
        title = {'text': "Tenuta del Credito (DSCR)"},
        gauge = {'axis': {'range': [0, 3]},
                 'steps': [
                     {'range': [0, 1.2], 'color': "red"},
                     {'range': [1.2, 3], 'color': "green"}]}))
    st.plotly_chart(fig, use_container_width=True)

    # D
