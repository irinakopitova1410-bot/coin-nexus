import streamlit as st
import plotly.graph_objects as go
from supabase import create_client, Client
import pandas as pd
from fpdf import FPDF

# --- CONFIGURAZIONE INTERFACCIA ---
st.set_page_config(page_title="Coin-Nexus Terminal", layout="wide", page_icon="🏛️")

# --- CONNESSIONE DATABASE (CLOUD SYNC) ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Configurazione Database non trovata. Verifica i 'Secrets' su Streamlit Cloud.")
    st.stop()

# --- MOTORE REPORT BANCARIO (PDF) ---
def crea_report_bancario(azienda, rating, m):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Istituzionale
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"DOSSIER DI RATING: {azienda.upper()}", ln=True, align='L')
    pdf.set_font("Arial", 'I', 9)
    pdf.cell(0, 5, f"Data Analisi: {pd.to_datetime('today').strftime('%d/%m/%Y')} | Protocollo: CN-PRIV", ln=True)
    pdf.ln(10)

    # Box Score Finale
    pdf.set_fill_color(235, 235, 235)
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 20, f"VALUTAZIONE FINALE: {rating}", 1, 1, 'C', True)
    pdf.ln(10)

    # Sintesi Finanziaria
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "1. SINTESI DEI PARAMETRI", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, f"Fatturato: EUR {m['rev']:,.0f}", ln=True)
    pdf.cell(0, 8, f"EBITDA: EUR {m['ebitda']:,.0f}", ln=True)
    pdf.cell(0, 8, f"Indice DSCR: {m['dscr']:.2f}", ln=True)
    
    # Stress Test (Scenario Avverso)
    pdf.ln(5)
    pdf.set_fill_color(255, 245, 245)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "2. STRESS TEST SCENARIO (-20%)", 1, 1, 'L', True)
    pdf.set_font("Arial", '', 10)
    stress_ebitda = (m['rev'] * 0.8) - (m['rev'] - m['ebitda'])
    resilienza = "ALTA" if stress_ebitda > 0 else "CRITICA"
    pdf.multi_cell(0, 8, f"In caso di contrazione dei ricavi del 20%, l'EBITDA stimato scenderebbe a EUR {stress_ebitda:,.0f}. Resilienza del modello: {resilienza}.")
    
    # Verdetto
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    verdetto = "CREDITO APPROVATO" if rating != "CCC" else "REVISIONE MANUALE"
    pdf.cell(0, 10, f"ESITO AUTOMATIZZATO: {verdetto}", 0, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

# --- MOTORE DI SCORING (LOGICA) ---
def esegui_audit(ricavi, costi, debito):
    ebitda = ricavi - costi
    dscr = ebitda / (debito if debito > 0 else 1)
    if dscr > 2.5: rating = "AAA"
    elif dscr > 1.2: rating = "BBB"
    else: rating = "CCC"
    return rating, dscr, ebitda

# --- SIDEBAR (INPUT DATI) ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/checked-user-male.png", width=80)
    st.header("Nexus Terminal")
    azienda = st.text_input("Ragione Sociale", "Azienda Esempio S.r.l.")
    ricavi = st.number_input("Ricavi (€)", value=1000000)
    costi = st.number_input("Costi Operativi (€)", value=80000
