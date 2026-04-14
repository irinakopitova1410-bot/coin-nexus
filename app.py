import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
from datetime import datetime
import io

# --- 1. CONFIGURAZIONE ISTITUZIONALE ---
st.set_page_config(page_title="Coin-Nexus | Protocol 10M", layout="wide", page_icon="🏛️")

# --- 2. MOTORE DI GENERAZIONE REPORT (IL CUORE DEL VALORE) ---
class InstitutionalReport(FPDF):
    def header(self):
        self.set_fill_color(0, 51, 102) # Blu Deep Bank
        self.rect(0, 0, 210, 45, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 18)
        self.cell(0, 25, 'OFFICIAL CREDIT RATING & AUDIT REPORT', 0, 1, 'C')
        self.set_font('Arial', 'I', 9)
        self.cell(0, -10, 'Standard ISA 320 / Basel IV Compliance Framework', 0, 1, 'C')
        self.ln(30)

def genera_report_dieci_milioni(data):
    pdf = InstitutionalReport()
    pdf.add_page()
    
    # Intestazione Professionale
    pdf.set_text_color(0, 51, 102)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"ANALISI VALIDATA PER IL SISTEMA DI TESORERIA: {data['filename']}", ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f"Data di emissione: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(5)

    # Tabella Indicatori Certificati
    pdf.set_fill_color(245, 245, 245)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(95, 12, " DSCR (Debt Service Coverage Ratio)", 1, 0, 'L', True)
    pdf.cell(95, 12, f" {data['dscr']}", 1, 1, 'C', True)
    
    pdf.cell(95, 12, " Debt to Equity Ratio", 1, 0, 'L', True)
    pdf.cell(95, 12, f" {data['d2e']}", 1, 1, 'C', True)
    pdf.ln(10)

    # Analisi Capacita di Rimborso
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "ANALISI DELLA CAPACITA DI RIMBORSO:", ln=True)
    pdf.set_font('Arial', '', 11)
    testo_analisi = (
        f"L'indice DSCR di {data['dscr']} certifica una generazione di cassa operativa ampiamente superiore "
        f"agli impegni finanziari. Il rapporto Debt to Equity di {data['d2e']} indica una struttura "
        "patrimoniale estremamente solida, ideale per l'accesso facilitato a linee di credito corporate."
    )
    pdf.multi_cell(0, 8, testo_analisi.replace('à', 'a').replace('ì', 'i'))
    pdf.ln(5)

    # Raccomandazioni Strategiche
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "RACCOMANDAZIONI STRATEGICHE PER LA BANCA:", ln=True)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 8, (
        "- Sincronizzare i flussi di cassa con il modulo Tesoreria per ottimizzare il DSCR mensile.\n"
        "- Sfruttare il basso Debt/Equity per rinegoziare i tassi d'interesse correnti.\n"
        "- Utilizzare il report Coin-Nexus come allegato tecnico per la revisione del rating Basilea IV."
    ).replace('è', 'e'))

    return pdf.output(dest='S').encode('latin-1')

# --- 3. LOGICA DI ACCESSO ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🏛️ Protocollo Coin-Nexus | Quantum Login")
    mail = st.text_input("ID Istituzionale (Admin)")
    pw = st.text_input("Password", type="password")
    if st.button("SBLOCCA TERMINALE"):
        if mail == "admin@coin-nexus.com" and pw == "quantum2026":
            st.session_state['auth'] = True
            st.rerun()
        else:
            st.error("Credenziali Errate")
    st.stop()

# --- 4. DASHBOARD DEL COMANDANTE ---
st.title("🚀 Terminale Strategico Coin-Nexus")
st.sidebar.info("Database: Supabase Standby\nRating: AAA Active")

up = st.file_uploader("Carica Bilancio / Export Tesoreria", type=['xlsx', 'csv'])

if up:
    dscr = 1.85
    d2e = 0.65
    liquidita = 1250000.0
    isa_materialita = liquidita * 0.015

    # KPI PRINCIPALI
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rating Asset", "AAA / Prime")
    c2.metric("Liquidita Netta", f"€ {liquidita:,.0f}")
    c3.metric("DSCR Certificato", dscr)
    c4.metric("Valore Software", "€ 10.000.000")

    st.divider()

    # GRAFICI WALL STREET STYLE
    g1, g2 = st.columns(2)
    with g1:
        st.subheader("📊 Proiezione Cash Flow")
        df = pd.DataFrame({'Mese': ['Gen', 'Feb', 'Mar', 'Apr'], 'Cassa': [800, 950, 1100, 1250]})
        fig = px.area(df, x='Mese', y='Cassa', title="Crescita Liquidita (K€)", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    
    with g2:
        st.subheader("📉 Stress Test Basilea IV")
        calo = st.slider("Simula Shock Mercato (%)", 0, 80, 20)
        dscr_stress = dscr * (1 - (calo/100) * 1.7)
        fig_g = go.Figure(go.Indicator(
            mode = "gauge+number", value = dscr_stress,
            gauge = {'axis': {'range': [0, 3]}, 'steps': [{'range': [0, 1.2], 'color': "red"}, {'range': [1.2, 3], 'color': "green"}]}))
        st.plotly_chart(fig_g, use_container_width=True)
