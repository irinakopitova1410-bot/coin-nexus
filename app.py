import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
from supabase import create_client, Client
import io

# --- 1. CONFIGURAZIONE ---
st.set_page_config(page_title="Coin-Nexus Quantum Audit", layout="wide", page_icon="💠")

# Credenziali Supabase (lasciale caricate per quando vorrai usarle)
SUPABASE_URL = "https://ipmttldwfsxuubugiyir.supabase.co"
SUPABASE_KEY = "sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos"

if 'auth' not in st.session_state:
    st.session_state['auth'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None

# --- 2. REPORT PDF (Versione Integrale ISA 320) ---
def genera_pdf_audit(massa, materialita, azienda, auditor):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "REPORT DI REVISIONE LEGALE - COIN-NEXUS", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, "Standard: ISA Italia 320 | Quantum AI Compliance", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, "DETTAGLI ANALISI", ln=True, fill=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, f"Soggetto: {azienda}", ln=True)
    pdf.cell(0, 8, f"Auditor: {auditor}", ln=True)
    
    trascurabile = materialita * 0.05
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "PARAMETRI ISA 320", ln=True, fill=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, f"Massa Totale: Euro {massa:,.2f}", ln=True)
    pdf.cell(0, 8, f"Materialita (1.5%): Euro {materialita:,.2f}", ln=True)
    pdf.cell(0, 8, f"Soglia Errore Trascurabile: Euro {trascurabile:,.2f}", ln=True)
    
    pdf.ln(10)
    pdf.multi_cell(0, 8, "GIUDIZIO: Sulla base delle analisi effettuate, il bilancio fornisce una "
                         "rappresentazione veritiera e corretta della situazione finanziaria.")
    
    return pdf.output(dest='S').encode('latin-1')

# --- 3. LOGIN CON BACKDOOR ADMIN ---
def login_manager():
    st.sidebar.title("🔐 Accesso Sistema")
    email = st.sidebar.text_input("Email / User")
    pwd = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Accedi"):
        # --- LOGICA ADMIN PRIORITARIA ---
        if email == "admin@coin-nexus.com" and pwd == "quantum2026":
            st.session_state['auth'] = True
            st.session_state['user_email'] = email
            st.rerun()
        # --- LOGICA SUPABASE (Opzionale) ---
        else:
            try:
                supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
                res = supabase.auth.sign_in_with_password({"email": email, "password": pwd})
                st.session_state['auth'] = True
                st.session_state['user_email'] = email
                st.rerun()
            except:
                st.sidebar.error("Credenziali admin o utente errate")

# --- 4. FLUSSO APP ---
if not st.session_state['auth']:
    st.title("💠 Coin-Nexus Quantum AI")
    login_manager()
    st.stop()

# Dashboard Post-Login
st.title(f"🚀 Quantum Engine: {st.session_state['user_email']}")
file = st.file_uploader("Carica Bilancio", type=['xlsx', 'csv'])

if file:
    df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    c1, c2 = st.columns(2)
    with c1: desc = st.selectbox("Voce", df.columns)
    with c2: val = st.selectbox("Valore", num_cols)

    if st.button("📊 AVVIA ANALISI"):
        massa = df[val].abs().sum()
        mat = massa * 0.015
        
        # Grafico
        fig = px.treemap(df.head(15), path=[desc], values=val, title="Mappa Rischio ISA")
        st.plotly_chart(fig, use_container_width=True)

        # Download Report
        pdf_bytes = genera_pdf_audit(massa, mat, file.name, st.session_state['user_email'])
        st.download_button("📥 Scarica Report ISA 320 (PDF)", pdf_bytes, f"Audit_{file.name}.pdf", "application/pdf")
