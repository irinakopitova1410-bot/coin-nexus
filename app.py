import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

# --- 1. CONFIGURAZIONE PAGINA (Deve essere la prima istruzione) ---
st.set_page_config(page_title="Coin-Nexus | Bank Intelligence", layout="wide", page_icon="🏦")

# --- 2. GESTIONE LOGIN ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("💠 Coin-Nexus | Quantum Access")
    col1, col2 = st.columns(2)
    with col1:
        u = st.text_input("User Admin")
        p = st.text_input("PIN di Sicurezza", type="password")
        if st.button("Sblocca Terminale"):
            if u == "admin" and p == "2026":
                st.session_state['auth'] = True
                st.rerun()
            else:
                st.error("Credenziali non valide")
    st.stop()

# --- 3. MOTORE PDF (Crash-Proof) ---
class BankReadyReport(FPDF):
    def header(self):
        self.set_fill_color(180, 0, 0) 
        self.rect(0, 0, 210, 45, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 18)
        self.cell(0, 25, 'DOSSIER DI CREDITO INTEGRATO - COIN-NEXUS', 0, 1, 'C')
        self.ln(20)

    def chapter_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, f" {label}", 0, 1, 'L', True)
        self.ln(4)

def clean_text(text):
    return text.replace('€', 'Euro').replace('à', 'a').replace('è', 'e').replace('é', 'e').replace('ì', 'i').replace('ò', 'o').replace('ù', 'u')

def genera_pdf_bank(data):
    pdf = BankReadyReport()
    pdf.add_page()
    pdf.chapter_title("1. SINTESI DI BANCABILITA (BASILEA IV)")
    pdf.set_font('Arial', '', 11)
    pdf.cell(95, 10, f"DSCR Prospettico: {data['dscr']}", 1)
    pdf.cell(95, 10, f"Debt/Equity Ratio: {data['d2e']}", 1, ln=True)
    pdf.cell(95, 10, f"Punto di Pareggio: Euro {data['bep']:,.0f}", 1)
    pdf.cell(95, 10, f"Grado di Rating: AAA", 1, ln=True)
    pdf.ln(5)
    pdf.chapter_title("2. ANALISI DI RESILIENZA")
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 7, clean_text(data['analisi']))
    pdf.ln(5)
    pdf.chapter_title("3. RACCOMANDAZIONI")
    for s in data['suggerimenti']:
        pdf.multi_cell(0, 7, f"- {clean_text(s)}")
    return pdf.output(dest='S').encode('latin-1')

# --- 4. DASHBOARD PRINCIPALE ---
st.title("🚀 Telepass Bancario
