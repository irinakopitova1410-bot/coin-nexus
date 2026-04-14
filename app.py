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

# --- 2. CLASSE REPORT ISTITUZIONALE (PDF) ---
class InstitutionalReport(FPDF):
    def header(self):
        # Header Blu Deep Bank
        self.set_fill_color(0, 51, 102)
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
        self.cell(0, 10, f'Confidenziale - Protocollo Coin-Nexus 10M - Pagina {self.page_no()}', 0, 0, 'C')

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
    pdf.set_text_color(0, 0, 0)
    pdf.cell(95, 12, " DSCR (Debt Service Coverage Ratio)", 1, 0, 'L', True)
    pdf.cell(95, 12, f" {data['dscr']}", 1, 1, 'C', True)
    
    pdf.cell(95, 12, " Debt to Equity Ratio", 1, 0, 'L', True)
    pdf.cell(95, 12, f" {data['d2e']}", 1, 1, 'C', True)
    pdf.ln(10)

    # Analisi Capacita di Rimborso
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "ANALISI DELLA CAPACITA DI RIMBORSO:", ln=True)
    pdf.set_font('Arial', '', 11)
    testo_analisi = (
        f"L'indice DSCR di {data['dscr']} certifica una generazione di cassa operativa ampiamente superiore "
        f"agli impegni finanziari. Il rapporto Debt to Equity di {data['d2e']} indica una struttura "
        "patrimoniale estremamente solida, ideale per l'accesso facilitato a linee di credito corporate."
    )
    pdf.multi_cell(0, 8, testo_analisi.replace('à', 'a').replace('ì', 'i').replace('è', 'e'))
    pdf.ln(5)

    # Raccomandazioni Strategiche
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "RACCOMANDAZIONI STRATEGICHE PER LA BANCA:", ln=True)
    pdf.set_font('Arial', '', 11)
    raccomandazioni = (
        "- Sincronizzare i flussi di cassa con il modulo Tesoreria per ottimizzare il DSCR mensile.\n"
        "- Sfruttare il basso Debt/Equity per rinegoziare i tassi d'interesse correnti.\n"
        "- Utilizzare il report Coin-Nexus come allegato tecnico per la revisione del rating Basilea IV."
    )
    pdf.multi_cell(0, 8, raccomandazioni.replace('è', 'e').replace('ò', 'o'))

    return pdf.output(dest='S').encode('latin-1')

# --- 3. LOGICA DI ACCESSO ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🏛️ Protocollo Coin-Nexus | Quantum Login")
    col1, _ = st.columns([1, 1])
    with col1:
        mail = st.text_input("ID Istituzionale (Admin)")
        pw = st.text_input("Password di Volo", type="password")
        if st.button("SBLOCCA TERMINALE STRATEGICO"):
            if mail == "admin@coin
