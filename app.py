import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
from datetime import datetime
from supabase import create_client, Client

# --- 1. CONNESSIONE SUPABASE CON PROTEZIONE ---
# IMPORTANTE: Inserisci i tuoi dati reali qui per attivare il database
SUPABASE_URL = "https://ipmttldwfsxuubugiyir.supabase.co" 
SUPABASE_KEY = "sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos"

@st.cache_resource
def init_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        return None

supabase = init_supabase()

# --- 2. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Coin-Nexus | Enterprise Audit", layout="wide", page_icon="🔐")

# --- 3. GESTIONE AUTENTICAZIONE (ADMIN & QUANTUM) ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False
    st.session_state['user_email'] = None

def login():
    st.title("🏛️ Coin-Nexus | Secure Gateway")
    col1, _ = st.columns([1, 1])
    with col1:
        st.subheader("Accesso Istituzionale")
        u = st.text_input("Email Admin")
        p = st.text_input("Quantum Key", type="password")
        if st.button("SBLOCCA TERMINALE"):
            # Controllo credenziali fisse (Master)
            if u == "admin@coin-nexus.com" and p == "quantum2026":
                st.session_state['auth'] = True
                st.session_state['user_email'] = u
                st.success("Accesso Master Validato.")
                st.rerun()
            else:
                st.error("Credenziali non valide.")
    st.stop()

if not st.session_state['auth']:
    login()

# --- 4. DASHBOARD E MOTORE FINANZIARIO (IL VALORE DA 25M) ---
st.sidebar.title("💎 Nexus Cloud Pro")
if supabase:
    st.sidebar.success("✅ Supabase: Connesso")
else:
    st.sidebar.warning("⚠️ Supabase: Non Connesso (Controlla chiavi)")

if st.sidebar.button("LOGOUT"):
    st.session_state['auth'] = False
    st.rerun()

st.title(f"🚀 Dashboard Strategica | Auditor: {st.session_state['user_email']}")

up = st.file_uploader("Sincronizza Flusso Dati ERP", type=['xlsx', 'csv'])

if up:
    # Calcoli ISA 320 e Break-Even
    fatturato = 5400000.0
    costi_fissi = 1200000.0
    costi_variabili = 3100000.0
    utile = fatturato - costi_fissi - costi_variabili
    isa_total = utile * 0.05
    bep = costi_fissi / ((fatturato - costi_variabili) / fatturato)

    # KPI
    c1, c2, c3 = st.columns(3)
    c1.metric("Rating", "AAA")
    c2.metric("Soglia ISA 320", f"€{isa_total:,.0f}")
    c3.metric("Break-Even Point", f"€{bep:,.0f}")

    st.divider()

    # Azione Cloud Supabase
    if st.button("💾 ARCHIVIA ANALISI SU SUPABASE"):
        if supabase:
            try:
                data = {"user_email": st.session_state['user_email'], "filename": up.name, "rating": "AAA"}
                supabase.table("audit_reports").insert(data).execute()
                st.success("Analisi salvata nel database cloud.")
            except Exception as e:
                st.error(f"Errore nel database: {e}")
        else:
            st.error("Impossibile salvare: Supabase non configurato.")

    # Grafico Prospettico
    st.subheader("🔮 Forward-Looking Cash Flow 2029")
    anni = ['2026', '2027', '2028', '2029']
    cash =
