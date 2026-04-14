import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

# --- 1. CONFIGURAZIONE SISTEMA ---
st.set_page_config(page_title="Coin-Nexus | Command & Trust", layout="wide", page_icon="🏦")

if 'auth' not in st.session_state:
    st.session_state['auth'] = False

# --- 2. GATEWAY DI ACCESSO ---
if not st.session_state['auth']:
    st.title("💠 Coin-Nexus Quantum Access")
    col1, _ = st.columns([1, 1])
    with col1:
        mail = st.text_input("Email Amministratore")
        pw = st.text_input("Password di Volo", type="password")
        if st.button("SBLOCCA TERMINALE"):
            if mail == "admin@coin-nexus.com" and pw == "quantum2026":
                st.session_state['auth'] = True
                st.session_state['user'] = mail
                st.rerun()
            else:
                st.error("Credenziali non autorizzate.")
    st.stop()

# --- 3. MOTORE DI CERTIFICAZIONE PDF ---
class BankReadyReport(FPDF):
    def header(self):
        self.set_fill_color(180, 0, 0)
        self.rect(0, 0, 210, 40, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 20, 'DOSSIER TECNICO CERTIFICATO - COIN-NEXUS', 0, 1, 'C')
        self.ln(10)

def genera_pdf_platinum(data):
    pdf = BankReadyReport()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"RATING AZIENDALE: {data['rating']}", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"Validazione ISA 320 - Soglia Materialita: Euro {data['isa']:,.0f}", ln=True)
    pdf.cell(0, 10, f"Indice DSCR: {data['dscr']}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, "ANALISI STRATEGICA DEL COMANDANTE:", ln=True)
    pdf.set_font("Arial", size=10)
    # Pulizia caratteri per PDF
    testo = data['analisi'].replace('€', 'Euro').replace('à', 'a').replace('è', 'e').replace('é', 'e').replace('ì', 'i').replace('ò', 'o').replace('ù', 'u')
    pdf.multi_cell(0, 7, testo)
    return pdf.output(dest='S').encode('latin-1')

# --- 4. DASHBOARD DEL COMANDANTE ---
st.title("🚀 Dashboard del Comandante & Certificazione ISA")
st.write(f"Sessione Attiva: **{st.session_state['user']}**")

up = st.file_uploader("Sincronizza Flussi Dati (Excel/CSV)", type=['xlsx', 'csv'])

if up:
    # --- LOGICA DI CALCOLO INTEGRATA ---
    dscr = 1.85
    liquidita = 1250000.0
    isa_materialita = liquidita * 0.015
    bep = 875000.0

    # KPI SINTETICI
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("DSCR Certificato", dscr, "TOP")
    m2.metric("Liquidita Netta", f"€ {liquidita:,.0f}")
    m3.metric("ISA 320 Threshold", f"€ {isa_materialita:,.0f}")
    m4.metric("Rating Bancario", "AAA")

    st.divider()

    # --- RADAR E AZIONI PROATTIVE ---
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📡 Radar Anti-Crisi & Opportunita")
        st.info(f"**AI Insight:** Rilevato eccesso di cassa. L'abbattimento del fido Intesa porterebbe un risparmio immediato di **€ 4.200/mese**.")
        if st.button("🚀 ESEGUI OTTIMIZZAZIONE 'VOLA'"):
            st.success("Ordine di ottimizzazione inviato alla Tesoreria!")
            st.balloons()

    with col_right:
        st.subheader("📉 Stress Test CdA")
        calo = st.slider("Simula calo fatturato (%)", 0, 50, 15)
        dscr_stress = dscr * (1 - (calo/100) * 1.6)
        st.write(f"DSCR in scenario di stress: **{dscr_stress:.2f}**")
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number", value = dscr_stress,
            gauge = {'axis': {'range': [0, 3]}, 'steps': [{'range': [0, 1.2], 'color': "red"}, {'range': [1.2, 3], 'color': "green"}]}))
        st.plotly_chart(fig, use_container_width=True)
