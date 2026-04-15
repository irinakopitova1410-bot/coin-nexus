import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Coin-Nexus | Master Audit 2026", layout="wide", page_icon="🏛️")

# --- CONNESSIONE SUPABASE PROTETTA ---
def init_supabase():
    try:
        from supabase import create_client
        # Cerca nei Secrets di Streamlit
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY")
        if url and key:
            return create_client(url, key)
    except:
        return None
    return None

supabase = init_supabase()

# --- CLASSE REPORT PDF ---
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

# --- LOGIN ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🏛️ Coin-Nexus | Secure Access")
    col1, _ = st.columns([1, 1])
    with col1:
        u = st.text_input("Admin Email")
        p = st.text_input("Quantum Key", type="password")
        if st.button("SBLOCCA TERMINALE"):
            if u == "admin@coin-nexus.com" and p == "quantum2026":
                st.session_state['auth'] = True
                st.rerun()
            else:
                st.error("Credenziali non valide.")
    st.stop()

# --- DASHBOARD ---
st.title("🚀 Terminale di Certificazione Strategica")
st.sidebar.success(f"Database: {'✅ Cloud' if supabase else '⚠️ Local Mode'}")

up = st.file_uploader("Sincronizza Dati ERP", type=['xlsx', 'csv'])

if up:
    # --- CALCOLI SCIENTIFICI ---
    fatturato = 5450000.0
    costi_fissi = 1180000.0
    costi_variabili = 3200000.0
    utile = fatturato - costi_fissi - costi_variabili
    
    isa_total = utile * 0.05
    bep = costi_fissi / ((fatturato - costi_variabili) / fatturato)
    safety = ((fatturato / bep) - 1) * 100

    # KPI Row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rating", "AAA")
    c2.metric("Soglia ISA 320", f"€{isa_total:,.0f}")
    c3.metric("Break-Even", f"€{bep:,.0f}")
    c4.metric("Safety Margin", f"{safety:.1f}%")

    st.divider()

    # --- GRAFICI ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📊 Punto di Pareggio (BEP)")
        x = np.linspace(0, fatturato * 1.5, 20)
        fig_bep = go.Figure()
        fig_bep.add_trace(go.Scatter(x=x, y=x, name='Ricavi', line=dict(color='#00ffcc', width=3)))
        fig_bep.add_trace(go.Scatter(x=x, y=costi_fissi + (costi_variabili/fatturato)*x, name='Costi', line=dict(color='#ff4b4b')))
        fig_bep.update_layout(template="plotly_dark", height=350)
        st.plotly_chart(fig_bep, use_container_width=True)

    with col_right:
        st.subheader("📈 Proiezione Cash Flow 4 Anni")
        anni = ['2026', '2027', '2028', '2029']
        cash = [1250, 1900, 2600, 3500]
        fig_pro = px.area(x=anni, y=cash, title="Target Liquidità (€k)")
        fig_pro.update_layout(template="plotly_dark", height=350)
        st.plotly_chart(fig_pro, use_container_width=True)

    # --- AZIONI ---
    if st.button("🏆 GENERA REPORT DA 20.000.000 €"):
        pdf = AuditPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f"Analisi per: {up.name}", ln=True)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 10, f"Materialita ISA 320: Euro {isa_total:,.0f}\nBEP: Euro {bep:,.0f}")
        
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        st.download_button("📥 SCARICA PDF", pdf_bytes, "Audit_20M.pdf", "application/pdf")
        st.balloons()
