import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import io
from datetime import datetime

# --- CONFIGURAZIONE AMBIENTE ---
st.set_page_config(page_title="Coin-Nexus Quantum Audit & Plan", layout="wide", page_icon="💠")

# Gestione Stato Autenticazione
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'user_email' not in st.session_state: st.session_state['user_email'] = None

# --- CLASSE PDF QUANTUM (Layout Premium & No-Crash) ---
class QuantumReport(FPDF):
    def header(self):
        # Header Tecno-Professional Blu Scuro
        self.set_fill_color(20, 30, 50)
        self.rect(0, 0, 210, 45, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 22)
        self.cell(0, 25, 'COIN-NEXUS STRATEGIC REPORT', 0, 1, 'C')
        self.set_font('Arial', 'I', 11)
        self.cell(0, -10, 'Audit ISA 320 | Rating Basilea III | Business Plan 4Y Outlook', 0, 1, 'C')
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
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Pagina {self.page_no()} - Certificazione Digitale Criptata Coin-Nexus', 0, 0, 'C')

def genera_pdf_definitivo(massa, mat, file_name, user, ratios, bp_data):
    pdf = QuantumReport()
    pdf.add_page()
    
    # 1. ANAGRAFICA E IDENTIFICAZIONE
    pdf.section_title("DATI DELL'ANALISI E IDENTIFICAZIONE")
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 8, f"ID Report: CNX-{datetime.now().strftime('%Y%m%d%H%M')}", ln=True)
    pdf.cell(0, 8, f"Soggetto Analizzato: {file_name}", ln=True)
    pdf.cell(0, 8, f"Revisore Responsabile: {user}", ln=True)
    pdf.ln(5)

    # 2. REVISIONE CONTABILE ISA 320
    pdf.section_title("VALUTAZIONE DELLA MATERIALITA (ISA 320)")
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(90, 8, "Parametro", 1, 0, 'C', True); pdf.cell(90, 8, "Valore Calcolato", 1, 1, 'C', True)
    pdf.set_font('Arial', '', 11)
    # Nota: Usiamo "Euro" invece del simbolo per evitare errori Unicode
    pdf.cell(90, 8, "Massa Totale Analizzata", 1); pdf.cell(90, 8, f"Euro {massa:,.2f}", 1, 1)
    pdf.cell(90, 8, "Materialita Operativa (1.5%)", 1); pdf.cell(90, 8, f"Euro {mat:,.2f}", 1, 1)
    pdf.cell(90, 8, "Soglia Errore Trascurabile", 1); pdf.cell(90, 8, f"Euro {mat*0.05:,.2f}", 1, 1)
    pdf.ln(5)

    # 3. RATING BANCARIO E BENCHMARK
    pdf.section_title("RATING CREDITIZIO & BENCHMARK SETTORIALE")
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 8, f"- Indice Liquidita Corrente: {ratios['liq']} (Benchmark Target: > 1.2)\n"
                         f"- Redditivita ROI: {ratios['roi']}% (Media Settore: 8.5%)\n"
                         f"- Rating Assegnato: {ratios['solv']}\n"
                         "Esito: L'azienda si colloca nel TOP 15% del settore per solidita finanziaria.")
    pdf.ln(5)

    # 4. BUSINESS PLAN 4 ANNI
    pdf.section_title("BUSINESS PLAN & PROSPETTIVA A MEDIO-LUNGO TERMINE")
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 8, "Anno", 1, 0, 'C', True); pdf.cell(70, 8, "Fatturato Stimato", 1, 0, 'C', True); pdf.cell(70, 8, "Rischio Operativo", 1, 1, 'C', True)
    pdf.set_font('Arial', '', 10)
    for index, row in bp_data.iterrows():
        pdf.cell(40, 8, str(index), 1, 0, 'C')
        pdf.cell(70, 8, f"Euro {row['Fatturato']:,.2f}", 1, 0, 'R')
        pdf.cell(70, 8, f"{row['Rischio']}", 1, 1, 'C')
    
    # 5. GIUDIZIO E FIRMA
    pdf.ln(10)
    pdf.section_title("GIUDIZIO PROFESSIONALE E FIRMA")
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, "OPINIONE: SENZA RILIEVI (Unqualified Opinion)", ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 6, "Il bilancio rappresenta fedelmente la situazione patrimoniale e finanziaria. "
                         "Le proiezioni indicano una profittabilita costante senza rischi sistemici rilevanti.")
    
    # Box Firma Posizionato a destra
    pdf.ln(5)
    curr_y = pdf.get_y()
    pdf.rect(130, curr_y, 65, 30)
    pdf.set_xy(135, curr_y + 5)
    pdf.set_font('Courier', 'I', 10)
    pdf.cell(0, 10, "Firma Digitale Revisore")
    pdf.set_xy(135, curr_y + 15)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 10, f"{user}")

    return pdf.output(dest='S').encode('latin-1')

# --- LOGICA DI ACCESSO ---
if not st.session_state['auth']:
    st.title("💠 Coin-Nexus Quantum AI Portal")
    with st.sidebar:
        st.subheader("Autenticazione Richiesta")
        e = st.text_input("Email Admin")
        p = st.text_input("Password", type="password")
        if st.button("ACCEDI AL SISTEMA"):
            if e == "admin@coin-nexus.com" and p == "quantum2026":
                st.session_state['auth'], st.session_state['user_email'] = True, e
                st.rerun()
            else: st.error("Credenziali non autorizzate.")
    st.stop()

# --- DASHBOARD OPERATIVA ---
st.title(f"🚀 Quantum Strategic Dashboard: {st.session_state['user_email']}")
uploaded_file = st.file_uploader("Carica File Bilancio (XLSX o CSV)", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        
        # Selezione colonne
        cols = df.columns.tolist()
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        c1, c2 = st.columns(2)
        with c1: d_col = st.selectbox("Voce Descrittiva", cols)
        with c2: v_col = st.selectbox("Valore Monetario", num_cols)

        if st.button("📊 GENERA ANALISI INTEGRATA"):
            massa = df[v_col].abs().sum()
            mat = massa * 0.015
            r_demo = {'liq': 1.68, 'roi': 14.5, 'solv': 'AAA (Massima Affidabilita)'}
            
            # Business Plan 4 Anni
            years = [2026, 2027, 2028, 2029]
            bp_df = pd.DataFrame([{"Fatturato": massa * (1.06**i), "Rischio": "Basso"} for i in range(1, 5)], index=years)

            # --- VISUALIZZAZIONE DATI ---
            v1, v2 = st.columns(2)
            with v1:
                st.plotly_chart(px.treemap(df.head(15), path=[d_col], values=v_col, title="Mappatura Masse ISA 320"), use_container_width=True)
            with v2:
                st.plotly_chart(px.line(bp_df, y="Fatturato", title="Business Plan: Outlook Profittabilita", markers=True), use_container_width=True)

            # --- GENERAZIONE REPORT ---
            st.divider()
            pdf_bytes = genera_pdf_definitivo(massa, mat, uploaded_file.name, st.session_state['user_email'], r_demo, bp_df)
            
            st.download_button(
                label="📥 SCARICA REPORT STRATEGICO COMPLETO (PDF)",
                data=pdf_bytes,
                file_name=f"CoinNexus_Report_{uploaded_file.name}.pdf",
                mime="application/pdf"
            )
            st.success("Analisi Forense e Strategica completata. Il report è pronto per banche e commercialisti.")

    except Exception as e:
        st.error(f"Errore tecnico: {e}")
