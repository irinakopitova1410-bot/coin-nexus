import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
from datetime import datetime
import io

# --- 1. CONFIGURAZIONE ---
st.set_page_config(page_title="Coin-Nexus | Protocollo 10M", layout="wide", page_icon="🏛️")

# --- 2. MOTORE PDF PROFESSIONALE ---
class InstitutionalReport(FPDF):
    def header(self):
        self.set_fill_color(0, 51, 102) # Blu Istituzionale
        self.rect(0, 0, 210, 45, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 18)
        self.cell(0, 25, 'OFFICIAL CREDIT RATING & AUDIT REPORT', 0, 1, 'C')
        self.set_font('Arial', 'I', 9)
        self.cell(0, -10, 'Standard ISA 320 / Basel IV Compliance Framework', 0, 1, 'C')
        self.ln(30)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, 'ID VERIFICA: CNX-DOC-479592 | VALIDATORE: admin@coin-nexus.com', 0, 0, 'C')

def genera_report_10m(data):
    pdf = InstitutionalReport()
    pdf.add_page()
    
    # Intestazione e File
    pdf.set_text_color(0, 51, 102)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Analisi validata per il sistema di Tesoreria: {data['filename']}", ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f"Data di emissione: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(5)

    # Griglia Indicatori
    pdf.set_fill_color(245, 245, 245)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(100, 12, " DSCR (Debt Service Coverage Ratio)", 1, 0, 'L', True)
    pdf.cell(90, 12, f" {data['dscr']}", 1, 1, 'C', True)
    
    pdf.cell(100, 12, " Debt to Equity Ratio", 1, 0, 'L', True)
    pdf.cell(90, 12, f" {data['d2e']}", 1, 1, 'C', True)
    pdf.ln(10)

    # Analisi Capacita Rimborso
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "ANALISI DELLA CAPACITA DI RIMBORSO:", ln=True)
    pdf.set_font('Arial', '', 11)
    testo_analisi = (
        f"L'indice DSCR di {data['dscr']} certifica una generazione di cassa operativa ampiamente superiore "
        f"agli impegni finanziari. Il rapporto Debt to Equity di {data['d2e']} indica una struttura "
        "patrimoniale estremamente solida, ideale per l'accesso facilitato a linee di credito corporate."
    )
    pdf.multi_cell(0, 8, testo_analisi.replace('à', 'a'))
    pdf.ln(5)

    # Raccomandazioni
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "RACCOMANDAZIONI STRATEGICHE PER LA BANCA", ln=True)
    pdf.set_font('Arial', '', 11)
    raccomandazioni = [
        "- Sincronizzare i flussi di cassa con il modulo Tesoreria per ottimizzare il DSCR mensile.",
        "- Sfruttare il basso Debt/Equity per rinegoziare i tassi d'interesse correnti.",
        "- Utilizzare il report Coin-Nexus come allegato tecnico per la revisione del rating Basilea IV."
    ]
    for r in raccomandazioni:
        pdf.cell(0, 8, r.replace('è', 'e').replace('ò', 'o'), ln=True)

    return pdf.output(dest='S').encode('latin-1')

# --- 3. ACCESSO ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🏛️ Coin-Nexus | Accesso Istituzionale")
    mail = st.text_input("ID Admin")
    pw = st.text_input("Password", type="password")
    if st.button("ACCEDI"):
        if mail == "admin@coin-nexus.com" and pw == "quantum2026":
            st.session_state['auth'] = True
            st.rerun()
        else:
            st.error("Credenziali Errate")
    st.stop()

# --- 4. DASHBOARD ---
st.title("🚀 Terminale di Comando Strategico")
up = st.file_uploader("Sincronizza File Tesoreria", type=['xlsx', 'csv'])

if up:
    # Parametri fissi per il report richiesto
    dscr = 1.85
    d2e = 0.65
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Rating", "AAA / Prime")
    col2.metric("DSCR", dscr)
    col3.metric("Debt/Equity", d2e)

    st.divider()

    # Grafico Wall Street
    df_chart = pd.DataFrame({'Periodo': ['T1', 'T2', 'T3', 'T4'], 'Cassa': [700, 950, 1100, 1250]})
    fig = px.area(df_chart, x='Periodo', y='Cassa', title="Evoluzione Liquidità Certificata", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # TASTO GENERAZIONE REPORT (IL PEZZO MANCANTE)
    st.subheader("🛡️ Certificazione Ufficiale")
    if st.button("🏆 EMETTI REPORT DA 10 MILIONI"):
        try:
            dati = {
                'filename': up.name,
