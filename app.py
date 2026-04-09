import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime
import numpy as np

# 1. CONFIGURAZIONE E STILE
st.set_page_config(page_title="COIN-NEXUS | ULTIMATE AUDIT", layout="wide")

st.markdown("""
    <style>
    .main { background: #030712; color: #f9fafb; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background: #0b0f1a; border-right: 1px solid #1e40af; }
    .stMetric { background: #111827; border: 1px solid #3b82f6; border-radius: 12px; padding: 20px !important; }
    h1 { font-weight: 800; text-transform: uppercase; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGICA PDF
class AuditPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "COIN-NEXUS AUDIT - REPORT PROFESSIONALE", ln=True, align="L")
        self.line(10, 20, 200, 20)
        self.ln(10)

def genera_pdf(data):
    pdf = AuditPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 15, "RELAZIONE DI REVISIONE INDIPENDENTE", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1. GIUDIZIO", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 10, f"Opinione: {data.get('opinione', 'N/D')}. Basandoci sui test effettuati, il bilancio rappresenta correttamente la situazione finanziaria.")
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. PARAMETRI ISA 320 & 570", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 10, f"Materialita Calcolata: Euro {data.get('mat', 0):,.2f}", ln=True)
    pdf.cell(0, 10, f"Indice Going Concern (DSCR): {data.get('dscr', 0):.2f}", ln=True)
    
    return pdf.output(dest='S')

# 3. SIDEBAR E DATI
st.sidebar.title("⚡ NEBULA-X")
menu = st.sidebar.radio("SISTEMI", [
    "💎 MONITOR", 
    "⚖️ MATERIALITÀ", 
    "🛡️ GOING CONCERN", 
    "📄 GENERATORE"
])

uploaded_file = st.sidebar.file_uploader("CARICA DATI", type=['xlsx', 'csv'])

# Inizializzazione session_state per non perdere i dati tra i menu
if 'mat' not in st.session_state: st.session_state['mat'] = 15000.0
if 'dscr' not in st.session_state: st.session_state['dscr'] = 1.5
if 'bench' not in st.session_state: st.session_state['bench'] = "Totale Attivo"

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        df.columns = [str(c).upper().strip() for c in df.columns]
    except:
        df = pd.DataFrame({'VOCE': ['Liquidità', 'Debiti'], 'VALORE': [500000, 200000]})
else:
    df = pd.DataFrame({'VOCE': ['Liquidità', 'Crediti', 'Debiti'], 'VALORE': [500000, 300000, 200000]})

val_col = df.columns[1]

# --- MODULI ---

if menu ==
