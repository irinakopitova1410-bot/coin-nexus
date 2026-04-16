import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
from fpdf import FPDF

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="Nexus Enterprise | AI Risk Management",
    page_icon="🏛️",
    layout="wide"
)

# Inizializzazione Session State per evitare crash al refresh
if 'pdf_ready' not in st.session_state:
    st.session_state.pdf_ready = None

# --- 2. MOTORI DI CALCOLO (LOGICA SAAS) ---

def run_financial_engine(rev, ebitda, debt):
    """Calcola tutti i parametri finanziari in un colpo solo"""
    # KPI Base
    rev = max(rev, 1)
    margin = (ebitda / rev) * 100
    dscr = ebitda / (debt * 0.12 + 1) # Stress test al 12%
    
    # Altman Z-Score (Adattato PMI)
    x1 = (rev * 0.1) / max(debt, 1)
    x2 = (ebitda * 0.4) / max(debt, 1)
    x3 = ebitda / max(debt, 1)
    z_score = (1.2 * x1) + (1.4 * x2) + (3.3 * x3)
    
    # Decision Engine
    if z_score > 2.6 and dscr > 1.2:
        decision = {"status": "APPROVATO", "color": "#00CC66", "risk": "Basso"}
    elif z_score > 1.1:
        decision = {"status": "REVISIONE", "color": "#FFA500", "risk": "Moderato"}
    else:
        decision = {"status": "RESPINTO", "color": "#FF4B4B", "risk": "Alto"}
        
    return {
        "margin": margin, "dscr": dscr, "z_score": z_score,
        "decision": decision, "credit_limit": ebitda * 0.6
    }

# --- 3. SIDEBAR (INPUT) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/584/584011.png", width=80)
    st.title("Nexus Control Panel")
    st.markdown("---")
    
    company_name = st.text_input("Ragione Sociale", "Azienda Esempio S.p.A.")
    rev_in = st.number_input("Fatturato (€)", value=1200000, step=10000)
    ebit_in = st.number_input("EBITDA (€)", value=250000, step=5000)
    pfn_in = st.number_input("Debito Totale (€)", value=450000, step=5000)
    
    st.markdown("---")
    st.caption("Nexus Enterprise v3.0 | Real-time Scoring")

# --- 4. LAYOUT PRINCIPALE ---
st.title("🏛️ Nexus Enterprise: AI Financial Intelligence")
st.info("Strumento di analisi predittiva del rischio e automazione del credito.")

# Pulsante di calcolo
if st.button("🚀 GENERA ANALISI E REPORT", use_container_width=True):
    results = run_financial_engine(rev_in, ebit_in, pfn_in)
    
    # A. SEZIONE DECISIONALE
    st.divider()
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        st.subheader("💰 Decision Engine")
        st.markdown(f"""
            <div style="background-color:{
