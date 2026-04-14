import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
from supabase import create_client, Client
import io

# --- 1. CONFIGURAZIONE E CONNESSIONE ---
st.set_page_config(page_title="Coin-Nexus Quantum Audit", layout="wide", page_icon="💠")

# Inserisci i tuoi dati reali che trovi su Supabase (Project Settings > API)
SUPABASE_URL = "https://ipmttldwfsxuubugiyir.supabase.co"
SUPABASE_KEY = "sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos"

# Inizializziamo il client Supabase una sola volta
@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

if 'auth' not in st.session_state:
    st.session_state['auth'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None

# --- 2. FUNZIONE PDF (Manteniamo la logica professionale) ---
def genera_pdf_audit(massa, materialita, azienda, auditor):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "REPORT DI REVISIONE LEGALE - QUANTUM AI", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "DETTAGLI ISA 320", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, f"Soggetto: {azienda}", ln=True)
    pdf.cell(0, 8, f"Auditor: {auditor}", ln=True)
    pdf.cell(0, 8, f"Massa Totale: Euro {massa:,.2f}", ln=True)
    pdf.cell(0, 8, f"Materialita (1.5%): Euro {materialita:,.2f}", ln=True)
    pdf.multi_cell(0, 8, "\nGiudizio: Il bilancio fornisce una rappresentazione veritiera e corretta.")
    return pdf.output(dest='S').encode('latin-1')

# --- 3. LOGICA LOGIN & REGISTRAZIONE CON MAIL ---
def login_manager():
    st.sidebar.title("🔐 Accesso Quantum Audit")
    tab1, tab2 = st.sidebar.tabs(["Accedi", "Registrati"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        pwd = st.text_input("Password", type="password", key="login_pwd")
        if st.button("Log In"):
            try:
                # Supabase controlla se l'utente esiste e ha confermato la mail
                res = supabase.auth.sign_in_with_password({"email": email, "password": pwd})
                st.session_state['auth'] = True
                st.session_state['user_email'] = email
                st.rerun()
            except Exception as e:
                st.error("Accesso fallito: controlla email e password (o conferma la mail).")

    with tab2:
        new_email = st.text_input("Nuova Email", key="reg_email")
        new_pwd = st.text_input("Scegli Password", type="password", key="reg_pwd")
        if st.button("Crea Account"):
            try:
                # Questo comando invia AUTOMATICAMENTE la mail di conferma
                supabase.auth.sign_up({"email": new_email, "password": new_pwd})
                st.success(f"📧 Mail di conferma inviata a {new_email}! Controlla la tua posta.")
            except Exception as e:
                st.error(f"Errore registrazione: {e}")

# --- 4. FLUSSO DELL'APP ---
if not st.session_state['auth']:
    st.title("💠 Coin-Nexus Quantum AI")
    st.info("Benvenuto nel sistema di Audit Certificato. Registrati o accedi per iniziare.")
    login_manager()
    st.stop()

# Dashboard principale (accessibile solo dopo login)
st.title(f"🚀 Dashboard di {st.session_state['user_email']}")
if st.sidebar.button("Log Out"):
    st.session_state['auth'] = False
    st.rerun()

file = st.file_uploader("Carica Bilancio", type=['xlsx', 'csv'])
if file:
    df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    col1, col2 = st.columns(2)
    with col1: desc = st.selectbox("Voce", df.columns)
    with col2: val = st.selectbox("Valore", num_cols)

    if st.button("📊 ANALIZZA"):
        massa = df[val].abs().sum()
        mat = massa * 0.015
        
        # Grafico
        fig = px.treemap(df.head(10), path=[desc], values=val, title="Mappatura ISA")
        st.plotly_chart(fig)

        # Report
        pdf_bytes = genera_pdf_audit(massa, mat, file.name, st.session_state['user_email'])
        st.download_button("📥 Scarica Report PDF", pdf_bytes, f"Audit_{file.name}.pdf", "application/pdf")
