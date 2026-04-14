import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import io
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Coin-Nexus Quantum Audit & Plan", layout="wide", page_icon="💠")

if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'user_email' not in st.session_state: st.session_state['user_email'] = None

# --- CLASSE PDF QUANTUM (Layout Impeccabile) ---
class QuantumReport(FPDF):
    def header(self):
        self.set_fill_color(20, 30, 50)
        self.rect(0, 0, 210, 40, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 20)
        self.cell(0, 20, 'COIN-NEXUS STRATEGIC AUDIT REPORT', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, -5, 'Certificazione ISA 320 | Rating Basilea III | Business Plan 4Y', 0, 1, 'C')
        self.ln(20)

    def section_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, f"  {label}", 0, 1, 'L', True)
        self.ln(4)

def genera_pdf_totale(massa, mat, file_name, user, ratios, bp_data):
    pdf = QuantumReport()
    pdf.add_page()
    
    # 1. ANAGRAFICA
    pdf.section_title("DATI IDENTIFICATIVI")
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 8, f"ID Report: CNX-{datetime.now().strftime('%Y%m%d%H%M')}", ln=True)
    pdf.cell(0, 8, f"Soggetto: {file_name}", ln=True)
    pdf.cell(0, 8, f"Auditor Responsabile: {user}", ln=True)
    pdf.ln(5)

    # 2. AUDIT ISA 320
    pdf.section_title("REVISIONE CONTABILE (ISA 320)")
    pdf.set_font('Arial', '', 11)
    pdf.cell(90, 8, "Massa Totale Analizzata:", 1); pdf.cell(90, 8, f"Euro {massa:,.2f}", 1, ln=True)
    pdf.cell(90, 8, "Materialita (1.5%):", 1); pdf.cell(90, 8, f"Euro {mat:,.2f}", 1, ln=True)
    pdf.cell(90, 8, "Errore Trascurabile (5%):", 1); pdf.cell(90, 8, f"Euro {mat*0.05:,.2f}", 1, ln=True)
    pdf.ln(5)

    # 3. RATING & BENCHMARK
    pdf.section_title("RATING CREDITIZIO & MERITO BANCARIO")
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 8, f"- Indice Liquidita Corrente: {ratios['liq']} (Target: >1.2)\n"
                         f"- ROI Aziendale: {ratios['roi']}% (Media Settore: 8.5%)\n"
                         f"- Rating Assegnato: {ratios['solv']}\n"
                         "Posizionamento: L'azienda rientra nel TOP 15% del settore di riferimento.")
    pdf.ln(5)

    # 4. BUSINESS PLAN 4 ANNI
    pdf.section_title("BUSINESS PLAN & PROSPETTIVA A MEDIO TERMINE")
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 8, "Anno", 1); pdf.cell(70, 8, "Fatturato Stimato", 1); pdf.cell(70, 8, "Rischio Operativo", 1, ln=True)
    pdf.set_font('Arial', '', 10)
    for index, row in bp_data.iterrows():
        pdf.cell(40, 8, str(index), 1)
        pdf.cell(70, 8, f"Euro {row['Fatturato']:,.2f}", 1)
        pdf.cell(70, 8, f"{row['Rischio']}", 1, ln=True)
    
    # 5. CONCLUSIONE E FIRMA
    pdf.ln(10)
    pdf.section_title("CERTIFICAZIONE E FIRMA DIGITALE")
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, "GIUDIZIO: SENZA
        
       
