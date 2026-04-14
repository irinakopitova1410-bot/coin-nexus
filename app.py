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

# --- CLASSE PDF QUANTUM (Anti-Crash & Pro Layout) ---
class QuantumReport(FPDF):
    def header(self):
        self.set_fill_color(20, 30, 50)
        self.rect(0, 0, 210, 45, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 22)
        self.cell(0, 25, 'COIN-NEXUS STRATEGIC REPORT', 0, 1, 'C')
        self.set_font('Arial', 'I', 11)
        self.cell(0, -10, 'Audit ISA 320 - Rating Basilea III - Business Plan 4Y', 0, 1, 'C')
        self.ln(25)

    def section_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(235, 235, 235)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, f"  {label}", 0, 1, 'L', True)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()} - Certificazione Digitale Coin-Nexus', 0, 0, 'C')

def genera_pdf_totale(massa, mat, file_name, user, ratios, bp_data):
    pdf = QuantumReport()
    pdf.add_page()
    
    # 1. ANAGRAFICA
    pdf.section_title("IDENTIFICAZIONE ANALISI")
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 8, f"ID Report: CNX-{datetime.now().strftime('%Y%m%d%H%M')}", ln=True)
    pdf.cell(0, 8, f"Soggetto: {file_name}", ln=True)
    pdf.cell(0, 8, f"Auditor: {user}", ln=True)
    pdf.ln(5)

    # 2. AUDIT ISA 320
    pdf.section_title("MATERIALITA DI REVISIONE (ISA 320)")
    pdf.set_font('Arial', '', 11)
    # NOTA: Usiamo 'Euro' invece del simbolo grafico per evitare l'errore Unicode
    pdf.cell(90, 8, "Massa Totale Analizzata:", 1); pdf.cell(90, 8, f"Euro {massa:,.2f}", 1, ln=True)
    pdf.cell(90, 8, "Materialita (1.5%):", 1); pdf.cell(90, 8, f"Euro {mat:,.2f}", 1, ln=True)
    pdf.cell(90, 8, "Soglia Errore Trascurabile:", 1); pdf.cell(90, 8, f"Euro {mat*0.05:,.2f}", 1, ln=True)
    pdf.ln(5)

    # 3. RATING BANCARIO
    pdf.section_title("MERITO CREDITIZIO & RATING")
    pdf.multi_cell(0, 8, f"Indice Liquidita: {ratios['liq']} | ROI: {ratios['roi']}% | Rating: {ratios['solv']}\n
