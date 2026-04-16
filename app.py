import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client, Client
from fpdf import FPDF
import io

# --- 1. CONFIGURAZIONE E SETUP ---
st.set_page_config(page_title="Nexus Enterprise", layout="wide", page_icon="🏛️")

# Inizializzazione Session State per stabilità dati
if 'pdf_data' not in st.session_state:
    st.session_state.pdf_data = None
if 'metrics' not in st.session_state:
    st.session_state.metrics = None
if 'generated' not in st.session_state:
    st.session_state.generated = False

# Connessione Database
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except:
        return None

supabase = init_connection()

# --- 2. MOTORI TECNICI (LOGICA INTERNA) ---

def calculate_metrics(d):
    rev = d.get('revenue', 1)
    ebitda = d.get('ebitda', 0)
    debt = d.get('debt', 0)
    dscr = ebitda / (debt * 0.1 + 1)
    margin = (ebitda / rev) * 100
    return {"dscr": dscr, "margin": margin, "ebitda": ebitda, "debt": debt, "revenue": rev}

def extract_from_excel(df):
    cols = {c.lower(): c for c in df.columns}
    ext = {}
    if 'fatturato' in cols: ext['revenue'] = df[cols['fatturato']].sum()
    elif 'revenue' in cols: ext['revenue'] = df[cols['revenue']].sum()
    if 'ebitda' in cols: ext['ebitda'] = df[cols['ebitda']].sum()
    elif 'mol' in cols: ext['ebitda'] = df[cols['mol']].sum()
    if 'debiti' in cols: ext['debt'] = df[cols['debiti']].sum()
    elif 'debt' in cols: ext['debt'] = df[cols['debt']].sum()
    return ext

# --- 3. MOTORE DECISIONALE (PILASTRO SAAS) ---
def get_decision_engine(m):
    score = 0
    if m['dscr'] > 1.25: score += 40
    if m['margin'] > 15: score += 30
    if m['ebitda'] > 500000: score += 30
    
    # Limite di credito automatico: 50% dell'EBITDA
    limit_credit = m['ebitda'] * 0.5 
    
    if score >= 70:
        return {"status": "APPROVATO", "color": "#00CC66", "limit": limit_credit}
    elif score >= 40:
        return {"status": "REVISIONE UMANA", "color": "#FFA500", "limit": limit_credit * 0.3}
    else:
        return {"status": "RESPINTO", "color": "#FF4B4B", "limit": 0}

# --- 4. MOTORE PDF (OUTPUT CERTIFICATO) ---
def create_pdf_bytes(nome, m):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(0, 10, "NEXUS ENTERPRISE - REPORT CERTIFICATO", ln=True, align='C')
    pdf.set_font("helvetica", '', 10)
    pdf.cell(0, 10, "Rating Merito Creditizio conforme ISA 320", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, f"Azienda: {nome}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("helvetica", '', 10)
    pdf.cell(90, 10, "Indicatore", 1); pdf.cell(90, 10, "Valore", 1, ln
