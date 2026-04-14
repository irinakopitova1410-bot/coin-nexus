import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime
import io

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Coin-Nexus | Telepass Bancario", layout="wide", page_icon="🏦")

# --- 2. MOTORE PDF (CRASH-PROOF) ---
class BankReport(FPDF):
    def header(self):
        self.set_fill_color(180, 0, 0) # Rosso Istituzionale
        self.rect(0, 0, 210, 45, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 25, 'CERTIFICAZIONE DI BANCABILITA - COIN-NEXUS', 0, 1, 'C')
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
    
    pdf.chapter("1. INDICATORI DI RATING (BASILEA IV)")
    pdf.set_font('Arial', '', 11)
    pdf.cell(95, 10, f"DSCR Prospettico: {data['dscr']}", 1)
    pdf.cell(95, 10, f"Debt/Equity Ratio: {data['d2e']}", 1, ln=True)
    pdf.cell(0, 10, f"Punto di Pareggio: Euro {data['bep']:,.0f}", 1, ln=True)
    
    pdf.ln(5)
    pdf.chapter("2. ANALISI DI RESILIENZA")
    pdf.set_font('Arial', '', 10)
    # Pulizia caratteri speciali per evitare errori
    testo = data['analisi'].replace('€', 'Euro').replace('à', 'a').replace('è', 'e').replace('é', 'e').replace('ì', 'i').replace('ò', 'o').replace('ù', 'u')
    pdf.multi_cell(0, 7, testo)
    
    pdf.ln(5)
    pdf.chapter("3. RACCOMANDAZIONI STRATEGICHE")
    for s in data['suggerimenti']:
        s_clean = s.replace('€', 'Euro').replace('à', 'a').replace('è', 'e').replace('é', 'e').replace('ì', 'i').replace('ò', '
