import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from supabase import create_client, Client

# --- 1. CONFIGURAZIONE ---
st.set_page_config(page_title="Coin-Nexus Quantum SaaS", layout="wide")

# Sostituisci con i tuoi dati Supabase reali
SUPABASE_URL = "https://ipmttldwfsxuubugiyir.supabase.co" 
SUPABASE_KEY = "sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos"

# Inizializzazione sessione per evitare KeyError
if 'auth' not in st.session_state:
    st.session_state['auth'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None

# --- 2. LOGICA DI AUTENTICAZIONE ---
def check_login(email, password):
    # Opzione A: Accesso rapido ADMIN (senza database)
    if email == "admin@coin-nexus.com" and password == "quantum2026":
        return True, email
    
    # Opzione B: Accesso tramite Supabase
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return True, email
    except:
        return False, None

# --- 3. INTERFACCIA LOGIN ---
if not st.session_state['auth']:
    st.title("💠 Coin-Nexus Quantum AI")
    st.sidebar.title("🔐 Login di Sistema")
    
    email_input = st.sidebar.text_input("Email / Username")
    pass_input = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Accedi"):
        success, email = check_login(email_input, pass_input)
        if success:
            st.session_state['auth'] = True
            st.session_state['user_email'] = email
            st.rerun()
        else:
            st.sidebar.error("Credenziali non valide")
    
    st.info("Benvenuto in Coin-Nexus. Usa le tue credenziali admin o registrati per accedere.")
    st.stop() # Blocca l'esecuzione qui finché non sei loggato

# --- 4. DASHBOARD (Visibile solo dopo il Login) ---
st.title(f"🚀 Dashboard di {st.session_state['user_email']}")

file = st.file_uploader("Carica Bilancio (Excel/CSV)", type=['xlsx', 'csv'])

if file:
    try:
        # Caricamento dati
        if file.name.endswith('.xlsx'):
            xl = pd.ExcelFile(file)
            sheet = st.selectbox("Seleziona Foglio", xl.sheet_names)
            df = xl.parse(sheet)
        else:
            df = pd.read_csv(file)

        st.subheader("🔍 Analisi Preliminare")
        
        # Selezione colonne
        col_desc, col_val = st.columns(2)
        with col_desc:
            descr_col = st.selectbox("Seleziona voce descrittiva", df.columns)
        with col_val:
            num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            val_col = st.selectbox("Seleziona colonna valori (€)", num_cols)

        if st.button("📊 AVVIA ANALISI"):
            massa = df[val_col].abs().sum()
            materialita = massa * 0.015 # Standard ISA 320
            
            # Risultati
            m1, m2 = st.columns(2)
            m1.metric("Massa Totale", f"€ {massa:,.2f}")
            m2.metric("Materialità (1.5%)", f"€ {materialita:,.2f}")
            
            # Grafico
            fig = px.bar(df.head(10), x=descr_col, y=val_col, title="Top 10 Voci di Bilancio")
            st.plotly_chart(fig, use_container_width=True)
            
            st.success("✅ Analisi completata con successo.")

    except Exception as e:
        st.error(f"Errore durante l'elaborazione: {e}")
