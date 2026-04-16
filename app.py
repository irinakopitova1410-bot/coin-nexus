import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client, Client
from fpdf import FPDF
import io

# --- 1. SETUP & CONNESSIONE ---
st.set_page_config(page_title="Nexus Enterprise", layout="wide", page_icon="🏛️")

# Inizializzazione Session State per evitare crash al refresh
if 'pdf_data' not in st.session_state:
    st.session_state.pdf_data = None
if 'metrics' not in st.session_state:
    st.session_state.metrics = None

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

try:
    supabase = init_connection()
except Exception as e:
    st.error(f"Errore Connessione: {e}")
    st.stop()

# --- 2. MOTORE DI CALCOLO E ESTRAZIONE ---
def internal_calculate_metrics(d):
    ebitda = d.get('ebitda', 0)
    debt = d.get('debt', 0)
    revenue = d.get('revenue', 1)
    dscr = ebitda / (debt * 0.1 + 1)
    margin = (ebitda / revenue) * 100
    return {"dscr": dscr, "margin": margin, "ebitda": ebitda, "debt": debt, "revenue": revenue}

def internal_extract_financials(df):
    cols = {c.lower(): c for c in df.columns}
    extracted = {}
    # Logica per trovare le colonne nei file ERP
    if 'fatturato' in cols: extracted['revenue'] = df[cols['fatturato']].sum()
    elif 'revenue' in cols: extracted['revenue'] = df[cols['revenue']].sum()
    if 'ebitda' in cols: extracted['ebitda'] = df[cols['ebitda']].sum()
    elif 'mol' in cols: extracted['ebitda'] = df[cols['mol']].sum()
    if 'debiti' in cols: extracted['debt'] = df[cols['debiti']].sum()
    elif 'debt' in cols: extracted['debt'] = df[cols['debt']].sum()
    return extracted

# --- 3. MOTORE PDF (CORRETTO) ---
def create_pdf_bytes(nome, m):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "NEXUS ENTERPRISE - DOSSIER CERTIFICATO", ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, "Standard ISA 320 / Basilea III", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Analisi per: {nome}", ln=True)
    pdf.ln(5)
    
    # Tabella Dati
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(90, 10, "Indicatore", 1)
    pdf.cell(90, 10, "Valore", 1, ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(90, 10, "Fatturato", 1); pdf.cell(90, 10, f"Euro {m['revenue']:,.2f}", 1, ln=True)
    pdf.cell(90, 10, "EBITDA", 1); pdf.cell(90, 10, f"Euro {m['ebitda']:,.2f}", 1, ln=True)
    pdf.cell(90, 10, "DSCR", 1); pdf.cell(90, 10, f"{m['dscr']:.2f}", 1, ln=True)
    pdf.cell(90, 10, "Margine %", 1); pdf.cell(90, 10, f"{m['margin']:.2f}%", 1, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 8
