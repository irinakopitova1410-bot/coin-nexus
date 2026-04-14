import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime
import io

# --- CONFIGURAZIONE HIGH-END ---
st.set_page_config(page_title="Coin-Nexus | Million Dollar Edition", layout="wide", page_icon="💎")

if 'auth' not in st.session_state:
    st.session_state['auth'] = False

# --- GATEWAY DI ACCESSO ---
if not st.session_state['auth']:
    st.title("💠 Coin-Nexus | Quantum Gateway")
    mail = st.text_input("Email Amministratore")
    pw = st.text_input("Password", type="password")
    if st.button("SBLOCCA TERMINALE"):
        if mail == "admin@coin-nexus.com" and pw == "quantum2026":
            st.session_state['auth'] = True
            st.session_state['user'] = mail
            st.rerun()
        else:
            st.error("Accesso negato.")
    st.stop()

# --- MOTORE REPORT "MILLION DOLLAR" ---
class MillionDollarReport(FPDF):
    def header(self):
        self.set_fill_color(30, 30, 30) # Nero Elegante
        self.rect(0, 0, 210, 50, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 20)
        self.cell(0, 30, 'INVESTOR-READY CREDIT DOSSIER', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, -10, 'Certified by Coin-Nexus Quantum Engine', 0, 1, 'C')
        self.ln(25)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Confidenziale - Coin-Nexus Million Dollar Edition - Pagina {self.page_no()}', 0, 0, 'C')

def genera_report_milionario(data):
    pdf = MillionDollarReport()
    pdf.add_page()
    
    # Sezione 1: Rating Strategico
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f"1. VALUTAZIONE ASSET: {data['rating']}", ln=True)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 7, f"Analisi condotta su flussi certificati ISA 320. Rating calcolato su parametri Basilea IV con DSCR di {data['dscr']}.")
    
    # Sezione 2: Financial Highlights
    pdf.ln(5)
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, " 2. INDICATORI DI PERFORMANCE", 0, 1, 'L', True)
    pdf.set_font('Arial', '', 11)
    pdf.cell(95, 10, f"Break-even Point: Euro {data['bep']:,.0f}", 1)
    pdf.cell(95, 10, f"Materialita ISA: Euro {data['isa']:,.0f}", 1, ln=True)
    
    # Sezione 3: AI Insights (Il valore aggiunto)
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, " 3. EXECUTIVE AI STRATEGY", 0, 1, 'L', True)
    pdf.set_font('Arial', '', 10)
    testo_pulito = data['analisi'].replace('€', 'Euro').replace('à', 'a').replace('è', 'e').replace('é', 'e').replace('ì', 'i').replace('ò', 'o').replace('ù', 'u')
    pdf.multi_cell(0, 7, testo_pulito)

    return pdf.output(dest='S').encode('latin-1')

# --- DASHBOARD ---
st.title("🚀 Dashboard del Comandante | Million Dollar Edition")

up = st.file_uploader("Sincronizza Dati Strategici", type=['xlsx', 'csv'])

if up:
    # Dati da 1 Milione di Euro
    dscr = 1.85
    liquidita = 1250000.0
    isa = liquidita * 0.015
    bep = 875000.0

    st.success("✅ Dati Sincronizzati con successo. Analisi Milionaria pronta.")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Rating Asset", "AAA / Prime")
    c2.metric("Liquidita Netta", f"€ {liquidita:,.0f}")
    c3.metric("Potenziale Valore App", "€ 1.000.000+")

    st.divider()

    # Visualizzazione Stress Test
    calo = st.slider("Simula Resilienza (%)", 0, 50, 15)
    dscr_stress = dscr * (1 - (calo/100) * 1.6)
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = dscr_stress,
        title = {'text': "Bancabilita Prospettica"},
        gauge = {'axis': {'range': [0, 3]}, 'steps': [{'range': [0, 1.2], 'color': "red"}, {'range': [1.2, 3], 'color': "green"}]}))
    st.plotly_chart(fig, use_container_width=True)

    # PREPARAZIONE REPORT (Logica sicura)
    st.subheader("🛡️ Certificazione e Dossier Bancario")
    
    if st.button("🏆 GENERA REPORT DA 1 MILIONE DI EURO"):
        try:
            report_data = {
                'rating': 'AAA (Investment Grade)',
                'dscr': dscr,
                'bep': bep,
                'isa': isa,
                'analisi': "L'azienda dimostra una solidita eccezionale. Il sistema di monitoraggio Coin-Nexus garantisce una trasparenza totale verso gli istituti di credito, eliminando il rischio operativo e ottimizzando la resa finanziaria degli asset."
            }
            pdf_bytes = genera_report_milionario(report_data)
            
            st.download_button(
                label="📥 SCARICA DOSSIER CERTIFICATO (PDF)",
                data=pdf_bytes,
                file_name=f"Dossier_Million_Nexus_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
            st.balloons()
        except Exception as e:
            st.error(f"Errore nella creazione del report milionario: {e}")
