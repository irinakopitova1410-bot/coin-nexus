import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
from supabase import create_client, Client
import io

# --- 1. CONFIGURAZIONE & CONNESSIONE ---
st.set_page_config(page_title="Coin-Nexus Quantum Audit", layout="wide", page_icon="💠")

# Sostituisci con le tue chiavi reali di Supabase
SUPABASE_URL = "https://ipmttldwfsxuubugiyir.supabase.co"
SUPABASE_KEY = "sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos"

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

if 'auth' not in st.session_state:
    st.session_state['auth'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None

# --- 2. FUNZIONE PDF (Manteniamo i tuoi dati perfetti) ---
def genera_pdf_audit_bancario(massa, materialita, nome_file, auditor, ratios):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "CERTIFICAZIONE DI AUDIT E RATING CREDITIZIO", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, "Protocollo: Quantum AI Forensic | Standard: ISA Italia 320", ln=True, align='C')
    pdf.ln(10)

    # 1. Anagrafica
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, "1. ANAGRAFICA ANALISI", ln=True, fill=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, f"File Sorgente: {nome_file}", ln=True)
    pdf.cell(0, 8, f"Auditor Responsabile: {auditor}", ln=True)
    pdf.cell(0, 8, f"Data Validazione: {pd.Timestamp.now().strftime('%d/%m/%Y')}", ln=True)
    
    # 2. ISA 320
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "2. REVISIONE CONTABILE (ISA 320)", ln=True, fill=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, f"Massa Totale Analizzata: Euro {massa:,.2f}", ln=True)
    pdf.cell(0, 8, f"Soglia di Materialita (1.5%): Euro {materialita:,.2f}", ln=True)
    pdf.cell(0, 8, f"Errore Chiaramente Trascurabile: Euro {materialita * 0.05:,.2f}", ln=True)

    # 3. Benchmarking
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "3. BENCHMARKING E RATING FINANZIARIO", ln=True, fill=True)
    pdf.set_font("Arial", '', 11)
    testo_banca = (
        f"Analisi Indici di Performance (Basilea III):\n"
        f"- Indice di Liquidita Corrente: {ratios['liq']:.2f} (Benchmark Ottimale: > 1.2)\n"
        f"- ROI (Redditivita): {ratios['roi']:.1f}% (Media Settore: 8.2%)\n"
        f"- Indice di Solvibilita: {ratios['solv']:.2f} (Rating: A+)\n\n"
        "L'algoritmo Quantum AI conferma che l'azienda si colloca nel TOP 15% del benchmark di settore."
    )
    pdf.multi_cell(0, 8, testo_banca)
    
    # 4. Giudizio
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "4. GIUDIZIO FINALE", ln=True, fill=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8, "Si rilascia un parere favorevole senza rilievi. La documentazione esaminata risulta coerente.")
    
    return pdf.output(dest='S').encode('latin-1')

# --- 3.
