import streamlit as st
import plotly.graph_objects as go
from supabase import create_client, Client
import pandas as pd
from fpdf import FPDF

# --- 1. CONFIGURAZIONE & STILE ---
st.set_page_config(page_title="Coin-Nexus Terminal", layout="wide", page_icon="🏛️")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { color: #00f2ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONNESSIONE DATABASE ---
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except:
        return None

supabase = init_connection()

# --- 3. MOTORE REPORT BANCARIO (PDF) ---
def create_banking_report(azienda, rating, m):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Istituzionale
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "COIN-NEXUS | FINANCIAL INTELLIGENCE REPORT", ln=True, align='C')
    pdf.ln(10)

    # Executive Summary Box
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 15, f"VALUTAZIONE FINALE: {rating}", 1, 1, 'C', True)
    pdf.ln(5)

    # Sezione 1: Snapshot Finanziario
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "1. SNAPSHOT FINANZIARIO", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f"Azienda: {azienda}", ln=True)
    pdf.cell(0, 8, f"Ricavi: EUR {m['rev']:,.0f}", ln=True)
    pdf.cell(0, 8, f"EBITDA: EUR {m['ebitda']:,.0f}", ln=True)
    pdf.cell(0, 8, f"Indice DSCR: {m['dscr']:.2f}", ln=True)

    # Sezione 2: Stress Test (Scenario -20%)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "2. STRESS TEST (SCENARIO -20% RICAVI)", ln=True)
    pdf.set_font("Arial", '', 10)
    stress_ebitda = (m['rev'] * 0.8) - (m['rev'] - m['ebitda'])
    resilienza = "ALTA" if stress_ebitda > 0 else "CRITICA"
    pdf.multi_cell(0, 8, f"In caso di calo del fatturato del 20%, l'EBITDA scenderebbe a EUR {stress_ebitda:,.0f}. Grado di resilienza: {resilienza}.")

    # Verdetto Finale
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    verdetto = "CREDITO APPROVATO" if rating != "CCC" else "REVISIONE RICHIESTA"
    pdf.cell(0, 15, f"DECISIONE FINALE: {verdetto}", 0, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

# --- 4. LOGICA DI AUDIT ---
def perform_audit(rev, costs, debt):
    ebitda = rev - costs
    dscr = ebitda / (debt if debt > 0 else 1)
    if dscr > 2.2: rating = "AAA"
    elif dscr > 1.2: rating = "BBB"
    else: rating = "CCC"
    return rating, dscr, ebitda

# --- 5. INTERFACCIA UTENTE ---
st.title("🏛️ Coin-Nexus | Banking Terminal")
st.caption("Protocollo Certificato Basel IV - Credit Risk Engine")

with st.sidebar:
    st.header("📥 Input Dati ERP")
    comp = st.text_input("Ragione Sociale", "Azienda Target S.p
