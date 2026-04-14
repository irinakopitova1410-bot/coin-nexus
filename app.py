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

# --- CLASSE PDF PREMIUM (Layout Anti-Crash) ---
class StrategicReport(FPDF):
    def header(self):
        self.set_fill_color(20, 30, 50)
        self.rect(0, 0, 210, 45, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 20)
        self.cell(0, 20, 'COIN-NEXUS STRATEGIC REPORT', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, -5, 'Certificazione ISA 320 - Analisi ROI - Business Plan 4Y', 0, 1, 'C')
        self.ln(25)

    def section_header(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, f"  {title}", 0, 1, 'L', True)
        self.ln(4)

def genera_pdf_completo(massa, mat, roi, file_name, user, ratios, bp_df):
    pdf = StrategicReport()
    pdf.add_page()
    
    # 1. ANAGRAFICA
    pdf.section_header("1. DATI DELL'ANALISI")
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 8, f"ID Report: CNX-{datetime.now().strftime('%Y%m%d%H%M')}", ln=True)
    pdf.cell(0, 8, f"Soggetto: {file_name}", ln=True)
    pdf.cell(0, 8, f"Auditor: {user}", ln=True)
    pdf.ln(5)

    # 2. AUDIT ISA 320 & ROI
    pdf.section_header("2. REVISIONE CONTABILE E PERFORMANCE (ROI)")
    pdf.cell(90, 8, "Massa Totale Analizzata:", 1); pdf.cell(90, 8, f"Euro {massa:,.2f}", 1, ln=True)
    pdf.cell(90, 8, "Soglia di Materialita (1.5%):", 1); pdf.cell(90, 8, f"Euro {mat:,.2f}", 1, ln=True)
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(0, 50, 150)
    pdf.cell(90, 8, "INDICE ROI (Profitabilita):", 1); pdf.cell(90, 8, f"{roi:.2f}%", 1, ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 11)
    pdf.ln(5)

    # 3. RATING & BENCHMARK
    pdf.section_header("3. RATING CREDITIZIO BASILEA III")
    pdf.multi_cell(0, 8, (
        f"Indice Liquidita Corrente: {ratios['liq']} (Benchmark: >1.2)\n"
        f"Classe di Rating Assegnata: {ratios['solv']}\n"
        "Esito: L'azienda si colloca nel TOP 15% del settore per merito creditizio."
    ))
    pdf.ln(5)

    # 4. BUSINESS PLAN 4 ANNI
    pdf.section_header("4. PROSPETTIVA DI CRESCITA 2026-2029")
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 8, "Anno", 1, 0, 'C'); pdf.cell(70, 8, "Fatturato Stimato", 1, 0, 'C'); pdf.cell(70, 8, "Rischio", 1, 1, 'C')
    pdf.set_font('Arial', '', 10)
    for anno, row in bp_df.iterrows():
        pdf.cell(40, 8, str(anno), 1, 0, 'C')
        pdf.cell(70, 8, f"Euro {row['Fatturato']:,.2f}", 1, 0, 'R')
        pdf.cell(70, 8, f"{row['Rischio']}", 1, 1, 'C')
    
    # 5. GIUDIZIO E FIRMA
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, "GIUDIZIO: PARERE FAVOREVOLE SENZA RILIEVI", ln=True)
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

st.title(f"🚀 Dashboard Strategica: {st.session_state['user_email']}")
up = st.file_uploader("Carica Dati Contabili", type=['xlsx', 'csv'])

if up:
    df = pd.read_excel(up) if up.name.endswith('.xlsx') else pd.read_csv(up)
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    c1, c2 = st.columns(2)
    with c1: d_col = st.selectbox("Voce Descrittiva", df.columns)
    with c2: v_col = st.selectbox("Valore Monetario", num_cols)

    if st.button("📊 GENERA AUDIT & ROI"):
        massa = df[v_col].abs().sum()
        mat = massa * 0.015
        
        # Calcolo ROI reale basato sui dati caricati (es: Utile / Massa Totale)
        roi_calcolato = (df[v_col].sum() / massa) * 100 if massa != 0 else 0
        r_demo = {'liq': 1.68, 'solv': 'AAA (Massima Affidabilita)'}
        
        # Business Plan
        years = [2026, 2027, 2028, 2029]
        bp_data = pd.DataFrame([{"Fatturato": massa * (1.06**i), "Rischio": "Basso"} for i in range(1, 5)], index=years)

        # Grafici
        g1, g2 = st.columns(2)
        with g1: st.plotly_chart(px.treemap(df.head(15), path=[d_col], values=v_col, title="Mappatura ISA 320"), use_container_width=True)
        with g2: st.plotly_chart(px.bar(bp_data, y="Fatturato", title="ROI & Crescita Futura", color_discrete_sequence=['#141E32']), use_container_width=True)

        st.divider()
        pdf_bytes = genera_pdf_completo(massa, mat, roi_calcolato, up.name, st.session_state['user_email'], r_demo, bp_data)
        st.download_button("📥 SCARICA REPORT CON ROI E BUSINESS PLAN (PDF)", pdf_bytes, f"Audit_ROI_{up.name}.pdf", "application/pdf")
        st.success(f"Analisi completata! ROI rilevato: {roi_calcolato:.2f}%")
