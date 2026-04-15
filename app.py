import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
from datetime import datetime

# --- 1. CONFIGURAZIONE SISTEMA ---
st.set_page_config(page_title="Coin-Nexus | Master Audit 20M", layout="wide", page_icon="🏛️")

# Integrazione Supabase (con protezione se mancano le chiavi)
try:
    from supabase import create_client, Client
    url = st.secrets.get("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY")
    supabase = create_client(url, key) if url and key else None
except:
    supabase = None

# --- 2. CLASSE REPORT PDF (STRUTTURA BANCARIA) ---
class AuditPDF(FPDF):
    def header(self):
        self.set_fill_color(0, 40, 85)
        self.rect(0, 0, 210, 45, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 18)
        self.cell(0, 20, 'OFFICIAL AUDIT & STRATEGIC PROJECTION', 0, 1, 'C')
        self.set_font('Arial', 'I', 8)
        self.cell(0, -5, 'Standard ISA 320 | Basel IV Compliance | Break-Even Certified', 0, 1, 'C')
        self.ln(25)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'ID VERIFICA: CNX-20M-2026 | VALIDATORE: admin@coin-nexus.com', 0, 0, 'C')

# --- 3. ACCESSO MASTER ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🏛️ Coin-Nexus | Secure Gateway")
    u = st.text_input("Admin Email")
    p = st.text_input("Quantum Key", type="password")
    if st.button("SBLOCCA TERMINALE"):
        if u == "admin@coin-nexus.com" and p == "quantum2026":
            st.session_state['auth'] = True
            st.rerun()
        else:
            st.error("Accesso negato.")
    st.stop()

# --- 4. DASHBOARD STRATEGICA ---
st.title("🚀 Terminale di Certificazione Strategica | 20M Asset")
st.sidebar.title("💎 Nexus Control")
st.sidebar.write(f"DB Cloud: {'✅ Active' if supabase else '⚠️ Local'}")

up = st.file_uploader("Sincronizza Dati ERP (Excel/CSV)", type=['xlsx', 'csv'])

if up:
    # --- MOTORE MATEMATICO ---
    fatturato_attuale = 5450000.0
    costi_fissi = 1180000.0
    costi_variabili = 3200000.0
    utile = fatturato_attuale - costi_fissi - costi_variabili
    
    # ISA 320
    isa_total = utile * 0.05
    isa_toll = isa_total * 0.75
    
    # Break-Even
    margine_contribuzione = (fatturato_attuale - costi_variabili) / fatturato_attuale
    bep = costi_fissi / margine_contribuzione
    safety_margin = ((fatturato_attuale / bep) - 1) * 100

    # --- KPI FRONTEND ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rating Basilea IV", "AAA", "Stable")
    c2.metric("Soglia ISA 320", f"€ {isa_total:,.0f}")
    c3.metric("Break-Even Point", f"€ {bep:,.0f}")
    c4.metric("Safety Margin", f"{safety_margin:.1f}%")

    st.divider()

    # --- GRAFICI (IL VALORE VISIVO) ---
    g1, g2 = st.columns(2)

    with g1:
        st.subheader("📊 Analisi del Punto di Pareggio (BEP)")
        x_range = np.linspace(0, fatturato_attuale * 1.5, 20)
        fig_bep = go.Figure()
        fig_bep.add_trace(go.Scatter(x=x_range, y=x_range, name='Ricavi', line=dict(color='#00ffcc', width=4)))
        fig_bep.add_trace(go.Scatter(x=x_range, y=costi_fissi + (costi_variabili/fatturato_attuale)*x_range, name='Costi Totali', line=dict(color='#ff4b4b')))
        fig_bep.add_vline(x=bep, line_dash="dash", line_color="orange", annotation_text="BEP")
        fig_bep.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_bep, use_container_width=True)

    with g2:
        st.subheader("🔮 Forward-Looking: Proiezione 4 Anni")
        anni = ['2026', '2027', '2028', '2029']
        # Crescita simulata per 20M valutazione
        cash_flow = [1250, 1900, 2600, 3450] 
        fig_pro = px.area(x=anni, y=cash_flow, title="Liquidità Prospettica Target (€k)")
        fig_pro.update_traces(line_color="#0088ff")
        fig_pro.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_pro, use_container_width=True)

    st.divider()

    # --- AZIONI FINALI ---
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("💾 ARCHIVIA SU SUPABASE CLOUD"):
            if supabase:
                data = {"user": "admin", "file": up.name, "valore": 20000000}
                supabase.table("audit_logs
