import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime
import numpy as np

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="COIN-NEXUS ULTIMATE", layout="wide")

if 'mat' not in st.session_state: st.session_state['mat'] = 15000.0
if 'dscr' not in st.session_state: st.session_state['dscr'] = 1.4

# --- STILE SIDEBAR ---
st.sidebar.markdown("<h1 style='color: #3b82f6;'>💠 COIN-NEXUS</h1>", unsafe_allow_html=True)
st.sidebar.caption("SISTEMA DI AUDIT INTELLIGENTE v8.5")

# --- FUNZIONE GENERAZIONE PDF ---
def genera_pdf(df, mat, dscr, z_score):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 15, "RELAZIONE DI REVISIONE INDIPENDENTE", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"Generato il: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="R")
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1. PARAMETRI DI MATERIALITA (ISA 320)", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 10, f"Soglia di errore tollerabile calcolata: Euro {mat:,.2f}", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. VALUTAZIONE CONTINUITA (ISA 570)", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 10, f"Indice DSCR: {dscr:.2f}", ln=True)
    pdf.cell(0, 10, f"Altman Z-Score: {z_score:.2f}", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "3. CONCLUSIONI", ln=True)
    pdf.set_font("Arial", "", 11)
    status = "NON RILEVATE ANOMALIE" if z_score > 1.8 else "RILEVATI RISCHI DI CONTINUITA"
    pdf.multi_cell(0, 10, f"Sulla base dei test eseguiti, l'opinione del sistema risulta: {status}.")
    return pdf.output()

# --- CARICAMENTO FILE ---
uploaded_file = st.sidebar.file_uploader("📥 CARICA BILANCIO (Excel o CSV)", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
        
        # Pulizia colonne
        df.columns = [str(c).upper().strip() for c in df.columns]
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        text_cols = df.select_dtypes(include=[object]).columns.tolist()
        
        if len(num_cols) > 0 and len(text_cols) > 0:
            val_col = num_cols[0]
            lab_col = text_cols[0]
        else:
            st.error("Il file non ha colonne compatibili (Testo + Numeri).")
            df = pd.DataFrame({'VOCE': ['Liquidità', 'Debiti'], 'VALORE': [100, 50]})
            val_col, lab_col = 'VALORE', 'VOCE'
    except Exception as e:
        st.sidebar.error(f"Errore caricamento: {e}")
        df = pd.DataFrame({'VOCE': ['Liquidità', 'Debiti'], 'VALORE': [100, 50]})
        val_col, lab_col = 'VALORE', 'VOCE'
else:
    # Dati DEMO
    df = pd.DataFrame({
        'VOCE': ['Cassa e Banche', 'Crediti Clienti', 'Rimanenze', 'Debiti For
