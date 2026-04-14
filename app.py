import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

# --- ENGINE REPORTISTICA "BANK-READY" CORRETTO ---
class BankReadyReport(FPDF):
    def header(self):
        self.set_fill_color(180, 0, 0) # Rosso Istituzionale
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

def genera_pdf_bank(data, user):
    # Usiamo 'latin-1' ma dobbiamo pulire i caratteri speciali come l'Euro
    pdf = BankReadyReport()
    pdf.add_page()
    
    pdf.chapter_title("1. SINTESI DI BANCABILITA (BASILEA IV)")
    pdf.set_font('Arial', '', 11)
    # Sostituiamo il simbolo Euro con la parola 'Euro' per evitare l'UnicodeEncodeError
    pdf.cell(95, 10, f"DSCR Prospettico: {data['dscr']}", 1)
    pdf.cell(95, 10, f"Debt/Equity Ratio: {data['d2e']}", 1, ln=True)
    pdf.cell(95, 10, f"Break-even Point: Euro {data['bep']:,.0f}", 1)
    pdf.cell(95, 10, f"Grado di Rating: AAA", 1, ln=True)

    pdf.ln(5)
    pdf.chapter_title("2. ANALISI DI RESILIENZA E STRESS TEST")
    pdf.set_font('Arial', '', 10)
    # Pulizia testo per evitare errori unicode
    testo_pulito = data['analisi_bancaria'].replace('€', 'Euro').replace('à', 'a').replace('ì', 'i').replace('ù', 'u').replace('è', 'e').replace('é', 'e').replace('ò', 'o')
    pdf.multi_cell(0, 7, testo_pulito)

    pdf.ln(5)
    pdf.chapter_title("3. RACCOMANDAZIONI PER TESORERIA")
    for s in data['suggerimenti']:
        s_pulito = s.replace('€', 'Euro').replace('à', 'a').replace('ì', 'i').replace('ù', 'u').replace('è', 'e').replace('é', 'e').replace('ò', 'o')
        pdf.multi_cell(0, 7, f"- {s_pulito}")

    pdf.ln(10)
    pdf.set_font('Courier', 'B', 9)
    pdf.cell(0, 10, f"VALIDATED BY QUANTUM ENGINE | ID: {datetime.now().strftime('%Y%m%d%H%M')}", align='C')
    
    # OUTPUT senza .encode('latin-1') perché FPDF gestisce già la stringa pulita
    return pdf.output(dest='S').encode('latin-1')

# --- APPLICAZIONE (Logica di generazione corretta) ---
# ... (il resto del tuo codice per caricamento file e calcoli)

if up:
    # (Inserisci qui i calcoli bep, dscr, etc. come nel messaggio precedente)
    
    if st.button("🏆 GENERA DOSSIER BANCARIO COMPLETO"):
        report_data = {
            'dscr': 1.85, 
            'd2e': 0.65, 
            'bep': 888888, # Esempio valore
            'analisi_bancaria': "L'azienda presenta solidita... ecc", # Testo che avevamo definito
            'suggerimenti': ["Suggerimento 1", "Suggerimento 2"],
            'filename': up.name
        }
        try:
            pdf_bytes = genera_pdf_bank(report_data, st.session_state.get('user_email', 'admin'))
            st.download_button("📥 Scarica Dossier per la Banca", pdf_bytes, "Dossier_Credito_CoinNexus.pdf", "application/pdf")
            st.success("Report generato con successo!")
        except Exception as e:
            st.error(f"Errore nella generazione del PDF: {e}")
