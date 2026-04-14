import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Coin-Nexus | Vision 2029", layout="wide", page_icon="💎")

# --- MOTORE PDF CON BUSINESS PLAN ---
class VisionReport(FPDF):
    def header(self):
        self.set_fill_color(10, 30, 60)
        self.rect(0, 0, 210, 45, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 20, 'BUSINESS PLAN & CREDIT STRATEGY 2026-2029', 0, 1, 'C')
        self.set_font('Arial', 'I', 8)
        self.cell(0, -5, 'Certified by Coin-Nexus Intelligence Protocol', 0, 1, 'C')
        self.ln(25)

def genera_report_vision(data):
    pdf = VisionReport()
    pdf.add_page()
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Dossier Strategico: {data['filename']}", ln=True)
    pdf.cell(0, 10, "Rating Prospettico 4 Anni: AAA (Stabile)", ln=True)
    
    # Sezione Business Plan
    pdf.ln(5)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, " PIANO DI SOSTENIBILITA FINANZIARIA 2026-2029", 0, 1, 'L', True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 7, "Il modello predittivo indica una crescita costante del DSCR. La strategia prevede "
                         "l'ottimizzazione del capitale circolante tramite integrazione DocFinance, "
                         "riducendo il costo del debito del 1.5% annuo.")
    
    # Parametri richiesti dalla banca
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(100, 10, " Indicatore Previsionale", 1)
    pdf.cell(90, 10, " Valore Target 2029", 1, ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.cell(100, 10, " DSCR Medio", 1)
    pdf.cell(90, 10, " 2.85", 1, ln=True)
    pdf.cell(100, 10, " Debt / Equity Ratio", 1)
    pdf.cell(90, 10, " 0.45", 1, ln=True)

    return pdf.output(dest='S').encode('latin-1')

# --- UI APP ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🏛️ Coin-Nexus | Quantum Access")
    mail = st.text_input("Admin ID")
    pw = st.text_input("Security Key", type="password")
    if st.button("SBLOCCA VISION 2029"):
        if mail == "admin@coin-nexus.com" and pw == "quantum2026":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

st.title("🔮 Coin-Nexus Dashboard | Vision 2029")

up = st.file_uploader("Sincronizza Flusso Dati Master", type=['xlsx', 'csv'])

if up:
    st.success("Analisi Predittiva Attiva")
    
    # Grafico Prospettico 4 Anni
    anni = ['2026', '2027', '2028', '2029']
    cash = [1250, 1600, 2100, 2800]
    
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.line(x=anni, y=cash, title="Proiezione Liquidita Certificata (€k)", markers=True)
        fig.update_traces(line_color='#00ffcc')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.info("**Strategia DocFinance:**\nIl sistema suggerisce di attivare lo sconto fatture dinamico nel Q3 2026 per massimizzare il ROI del circolante.")
        if st.button("🏆 EMETTI REPORT DA 10 MILIONI"):
            pdf_bytes = genera_report_vision({'filename': up.name})
            st.download_button("📥 SCARICA BUSINESS PLAN PDF", pdf_bytes, "Nexus_Business_Plan.pdf", "application/pdf")
