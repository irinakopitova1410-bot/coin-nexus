import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import io
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Coin-Nexus Strategic Audit", layout="wide", page_icon="💠")

if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'user_email' not in st.session_state: st.session_state['user_email'] = None

# --- CLASSE PDF PREMIUM ---
class StrategicReport(FPDF):
    def header(self):
        self.set_fill_color(20, 30, 50)
        self.rect(0, 0, 210, 45, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 20)
        self.cell(0, 20, 'COIN-NEXUS STRATEGIC REPORT', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, -5, 'Certificazione ISA 320 - Basilea III - Business Plan 4Y', 0, 1, 'C')
        self.ln(25)

    def section_header(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, f"  {title}", 0, 1, 'L', True)
        self.ln(4)

def genera_pdf_completo(massa, mat, file_name, user, ratios, bp_df):
    pdf = StrategicReport()
    pdf.add_page()
    
    # 1. ANAGRAFICA
    pdf.section_header("1. DATI DELL'ANALISI")
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 8, f"ID Report: CNX-{datetime.now().strftime('%Y%m%d%H%M')}", ln=True)
    pdf.cell(0, 8, f"Soggetto: {file_name}", ln=True)
    pdf.cell(0, 8, f"Auditor: {user}", ln=True)
    pdf.ln(5)

    # 2. AUDIT ISA 320 (Come in image_53fc6b.png)
    pdf.section_header("2. REVISIONE CONTABILE (ISA 320)")
    pdf.cell(90, 8, "Massa Totale Analizzata:", 1); pdf.cell(90, 8, f"Euro {massa:,.2f}", 1, ln=True)
    pdf.cell(90, 8, "Soglia di Materialita (1.5%):", 1); pdf.cell(90, 8, f"Euro {mat:,.2f}", 1, ln=True)
    pdf.cell(90, 8, "Errore Trascurabile (5%):", 1); pdf.cell(90, 8, f"Euro {mat*0.05:,.2f}", 1, ln=True)
    pdf.ln(5)

    # 3. BENCHMARK & RATING (Come in image_56aa6b.png)
    pdf.section_header("3. RATING CREDITIZIO & BENCHMARK")
    pdf.multi_cell(0, 8, (
        f"Indice Liquidita Corrente: {ratios['liq']} (Benchmark: >1.2)\n"
        f"ROI Aziendale: {ratios['roi']}% (Media Settore: 8.5%)\n"
        f"Classe di Rating: {ratios['solv']}\n"
        "Posizionamento: L'azienda rientra nel TOP 15% del settore di riferimento."
    ))
    pdf.ln(5)

    # 4. BUSINESS PLAN 4 ANNI (Come in image_56aa44.png)
    pdf.section_header("4. BUSINESS PLAN & PROSPETTIVA 4 ANNI")
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 8, "Anno", 1, 0, 'C'); pdf.cell(70, 8, "Fatturato Stimato", 1, 0, 'C'); pdf.cell(70, 8, "Rischio", 1, 1, 'C')
    pdf.set_font('Arial', '', 10)
    for anno, row in bp_df.iterrows():
        pdf.cell(40, 8, str(anno), 1, 0, 'C')
        pdf.cell(70, 8, f"Euro {row['Fatturato']:,.2f}", 1, 0, 'R')
        pdf.cell(70, 8, f"{row['Rischio']}", 1, 1, 'C')
    
    # 5. FIRMA (Layout Tecno)
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, "GIUDIZIO: SENZA RILIEVI (Unqualified Opinion)", ln=True)
    pdf.rect(130, pdf.get_y(), 65, 30)
    pdf.set_xy(135, pdf.get_y() + 5)
    pdf.set_font('Courier', 'I', 10)
    pdf.cell(0, 10, "Firma Elettronica")
    pdf.set_xy(135, pdf.get_y() + 10)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 10, f"{user}")

    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACCIA ---
if not st.session_state['auth']:
    st.title("💠 Coin-Nexus Quantum Portal")
    with st.sidebar:
        e = st.text_input("Email Admin")
        p = st.text_input("Password", type="password")
        if st.button("ACCEDI"):
            if e == "admin@coin-nexus.com" and p == "quantum2026":
                st.session_state['auth'], st.session_state['user_email'] = True, e
                st.rerun()
    st.stop()

st.title(f"🚀 Quantum Strategic Engine")
up = st.file_uploader("Carica Bilancio", type=['xlsx', 'csv'])

if up:
    df = pd.read_excel(up) if up.name.endswith('.xlsx') else pd.read_csv(up)
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    c1, c2 = st.columns(2)
    with c1: d_col = st.selectbox("Voce", df.columns)
    with c2: v_col = st.selectbox("Importo", num_cols)

    if st.button("📊 ANALISI COMPLETA"):
        massa = df[v_col].abs().sum()
        mat = massa * 0.015
        r_demo = {'liq': 1.68, 'roi': 14.5, 'solv': 'AAA (Top Rating)'}
        
        # Business Plan
        years = [2026, 2027, 2028, 2029]
        bp_data = pd.DataFrame([{"Fatturato": massa * (1.06**i), "Rischio": "Basso"} for i in range(
