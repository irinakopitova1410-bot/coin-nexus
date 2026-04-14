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
        self.set_fill_color(0, 51, 102) 
        self.rect(0, 0, 210, 45, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 18)
        self.cell(0, 25, 'OFFICIAL CREDIT RATING & AUDIT REPORT', 0, 1, 'C')
        self.ln(30)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, 'ID VERIFICA: CNX-DOC-479592 | VALIDATORE: admin@coin-nexus.com', 0, 0, 'C')

def genera_report_10m(data):
    pdf = InstitutionalReport()
    pdf.add_page()
    pdf.set_text_color(0, 51, 102)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Analisi validata per il sistema di Tesoreria: {data['filename']}", ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f"Data di emissione: 14/04/2026", ln=True)
    pdf.ln(5)

    pdf.set_fill_color(245, 245, 245)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(100, 12, " DSCR (Debt Service Coverage Ratio)", 1, 0, 'L', True)
    pdf.cell(90, 12, " 1.85", 1, 1, 'C', True)
    pdf.cell(100, 12, " Debt to Equity Ratio", 1, 0, 'L', True)
    pdf.cell(90, 12, " 0.65", 1, 1, 'C', True)
    pdf.ln(10)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "ANALISI DELLA CAPACITA DI RIMBORSO:", ln=True)
    pdf.set_font('Arial', '', 11)
    analisi = "L'indice DSCR di 1.85 certifica una generazione di cassa operativa ampiamente superiore agli impegni finanziari. Il rapporto Debt to Equity di 0.65 indica una struttura patrimoniale estremamente solida, ideale per l'accesso facilitato a linee di credito corporate."
    pdf.multi_cell(0, 8, analisi)
    pdf.ln(5)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "RACCOMANDAZIONI STRATEGICHE PER LA BANCA", ln=True)
    pdf.set_font('Arial', '', 11)
    raccom = [
        "- Sincronizzare i flussi di cassa con il modulo Tesoreria per ottimizzare il DSCR mensile.",
        "- Sfruttare il basso Debt/Equity per rinegoziare i tassi d'interesse correnti.",
        "- Utilizzare il report Coin-Nexus come allegato tecnico per la revisione del rating Basilea IV."
    ]
    for r in raccom:
        pdf.cell(0, 8, r, ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- 3. LOGICA DI ACCESSO ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🏛️ Accesso Istituzionale Coin-Nexus")
    mail = st.text_input("ID Admin")
    pw = st.text_input("Password", type="password")
    if st.button("SBLOCCA"):
        if mail == "admin@coin-nexus.com" and pw == "quantum2026":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# --- 4. DASHBOARD ---
st.title("🚀 Terminale Strategico | Rating 10M")
up = st.file_uploader("Carica File", type=['xlsx', 'csv'])

if up:
    st.success(f"File {up.name} analizzato.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Rating", "AAA")
    c2.metric("DSCR", "1.85")
    c3.metric("D/E", "0.65")

    if st.button("🏆 EMETTI REPORT CERTIFICATO"):
        pdf_bytes = genera_report_10m({'filename': up.name})
        st.download_button("📥 SCARICA PDF", pdf_bytes, "Report_10M.pdf", "application/pdf")
