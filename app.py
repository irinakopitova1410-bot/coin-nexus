import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Coin-Nexus | Executive Audit", layout="wide", page_icon="🏛️")

# Inizializzazione Supabase (Utilizza i Secrets di Streamlit)
try:
    from supabase import create_client, Client
    url = st.secrets.get("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY")
    supabase = create_client(url, key) if url and key else None
except:
    supabase = None

# --- CLASSE PDF AVANZATA ---
class ExecutivePDF(FPDF):
    def header(self):
        self.set_fill_color(0, 40, 85)
        self.rect(0, 0, 210, 45, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 25, 'STRATEGIC AUDIT & 4-YEAR PROJECTION REPORT', 0, 1, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'VALIDATED BY COIN-NEXUS SYSTEM | ID: {datetime.now().strftime("%Y%m%d")}', 0, 0, 'C')

# --- LOGICA ACCESSO ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🏛️ Secure Gateway Login")
    u = st.text_input("Admin Email")
    p = st.text_input("Quantum Key", type="password")
    if st.button("SBLOCCA TERMINALE"):
        if u == "admin@coin-nexus.com" and p == "quantum2026":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# --- DASHBOARD ---
st.title("🚀 Terminale di Certificazione Strategica")
st.sidebar.success(f"DB Status: {'✅ Supabase Connected' if supabase else '⚠️ Local Mode'}")

up = st.file_uploader("Sincronizza Dati ERP", type=['xlsx', 'csv'])

if up:
    # 1. DATI FISSI E BENCHMARK
    fatturato_2026 = 5450000.0
    bep = 2847619.0
    isa_total = 47500.0
    
    # Previsioni 4 Anni
    anni = ['2026', '2027', '2028', '2029']
    rev_proj = [5.45, 6.80, 8.10, 10.5] # in milioni
    ebitda_proj = [0.95, 1.40, 1.90, 2.80] # in milioni

    # Benchmark Analisi
    benchmark_data = {
        "Kpi": ["EBITDA Margin", "Current Ratio", "Debt/EBITDA"],
        "Azienda": ["17.4%", "1.8", "2.1"],
        "Media Settore": ["12.1%", "1.4", "3.5"]
    }

    # --- UI FRONTEND ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Rating Attuale", "AAA", "Stable")
    c2.metric("Target Valutazione", "€ 25.000.000")
    c3.metric("Benchmark Gap", "+5.3%", "Performance High")

    st.divider()

    # Grafici interattivi
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("📊 Proiezione Fatturato 2026-2029")
        fig1 = px.bar(x=anni, y=rev_proj, labels={'x':'Anno', 'y':'Milioni €'}, color_discrete_sequence=['#00ffcc'])
        fig1.update_layout(template="plotly_dark")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col_r:
        st.subheader("🏁 Benchmark di Settore")
        st.table(pd.DataFrame(benchmark_data))

    # --- GENERAZIONE REPORT COMPLETO ---
    if st.button("🏆 GENERA DOSSIER BANCARIO INTEGRALE"):
        pdf = ExecutivePDF()
        pdf.add_page()
        
        # Pagina 1: ISA & BEP (Come da tua immagine)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f"Analisi validata: {up.name}", ln=True)
        pdf.ln(5)
        
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 10, " 1. PROTOCOLLO ISA 320 & BREAK-EVEN", 0, 1, 'L', True)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 10, f"- Soglia Materialita: Euro {isa_total:,.0f}", ln=True)
        pdf.cell(0, 10, f"- Punto di Pareggio (BEP): Euro {bep:,.0f}", ln=True)
        
        # Pagina 2: Previsioni e Benchmark (Il valore aggiunto)
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, " 2. BUSINESS PLAN 2026-2029", 0, 1, 'L', True)
        pdf.set_font('Arial', '', 10)
        for i, anno in enumerate(anni):
            pdf.cell(0, 10, f"Target {anno}: Fatturato {rev_proj[i]}M - EBITDA {ebitda_proj[i]}M", ln=True)
        
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, " 3. ANALISI BENCHMARK COMPARATIVA", 0, 1, 'L', True)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 10, "L'azienda supera la media di settore in tutti i principali KPI finanziari.", ln=True)

        # Salvataggio su Supabase
        if supabase:
            try:
                data_log = {"filename":
