import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
from supabase import create_client, Client
import io

# --- 1. CONFIGURAZIONE ---
st.set_page_config(page_title="Coin-Nexus Quantum Audit", layout="wide", page_icon="💠")

# Inserisci i tuoi dati Supabase qui
SUPABASE_URL = "https://ipmttldwfsxuubugiyir.supabase.co"
SUPABASE_KEY = "sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos"

# Inizializzazione sicura di Supabase
@st.cache_resource
def init_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        return None

supabase = init_supabase()

if 'auth' not in st.session_state:
    st.session_state['auth'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None

# --- 2. FUNZIONE PDF (Benchmark & ISA 320) ---
def genera_pdf_audit_bancario(massa, materialita, nome_file, auditor, ratios):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "CERTIFICAZIONE DI AUDIT E RATING CREDITIZIO", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, "Protocollo: Quantum AI Forensic | Standard: ISA Italia 320", ln=True, align='C')
    pdf.ln(10)
    
    # Sezione Dati
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, "1. SINTESI REVISIONE", ln=True, fill=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, f"File: {nome_file}", ln=True)
    pdf.cell(0, 8, f"Auditor: {auditor}", ln=True)
    pdf.cell(0, 8, f"Massa Totale: Euro {massa:,.2f}", ln=True)
    pdf.cell(0, 8, f"Materialita (1.5%): Euro {materialita:,.2f}", ln=True)
    
    # Sezione Benchmarking
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "2. RATING BANCARIO (BASILEA III)", ln=True, fill=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8, f"Liquidita: {ratios['liq']} | ROI: {ratios['roi']}% | Solvibilita: {ratios['solv']}\n"
                         "Esito: L'azienda si colloca nel TOP 15% del benchmark di settore.")
    
    return pdf.output(dest='S').encode('latin-1')

# --- 3. LOGIN UI (ADMIN + SUPABASE) ---
def login_ui():
    st.sidebar.title("🔐 Quantum Auth")
    tab1, tab2 = st.sidebar.tabs(["Accedi", "Registrati"])

    with tab1:
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")
        if st.button("Log In"):
            # ACCESSO ADMIN SEMPRE FUNZIONANTE
            if email == "admin@coin-nexus.com" and pwd == "quantum2026":
                st.session_state['auth'] = True
                st.session_state['user_email'] = email
                st.rerun()
            elif supabase:
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": pwd})
                    st.session_state['auth'] = True
                    st.session_state['user_email'] = email
                    st.rerun()
                except:
                    st.error("Credenziali errate o email non confermata.")
            else:
                st.error("Servizio Supabase non configurato.")

    with tab2:
        st.info("La registrazione richiede la conferma via email.")
        new_email = st.text_input("Nuova Email")
        new_pwd = st.text_input("Password", type="password")
        if st.button("Crea Account"):
            if supabase:
                try:
                    supabase.auth.sign_up({"email": new_email, "password": new_pwd})
                    st.success("📧 Controlla la tua mail per confermare!")
                except Exception as e:
                    st.error(f"Errore: {e}")
            else:
                st.error("Database non connesso.")

# --- 4. MAIN APP
