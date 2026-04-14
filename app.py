import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
from supabase import create_client, Client

# --- 1. CONFIGURAZIONE E CONNESSIONE SUPABASE ---
st.set_page_config(page_title="Coin-Nexus Quantum SaaS", layout="wide")

# Sostituisci con le tue credenziali reali da Supabase Dashboard > Settings > API
SUPABASE_URL = "https://ipmttldwfsxuubugiyir.supabase.co"
SUPABASE_KEY = "sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos"

@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

# --- 2. GESTIONE SESSIONE ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None

# --- 3. FUNZIONE LOGIN ---
def login_supabase():
    st.sidebar.title("🔐 Accesso Professionale")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    
    c1, c2 = st.sidebar.columns(2)
    if c1.button("Accedi"):
        try:
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state['auth'] = True
            st.session_state['user_email'] = email
            st.rerun()
        except Exception:
            st.sidebar.error("Credenziali errate")
            
    if c2.button("Registrati"):
        try:
            supabase.auth.sign_up({"email": email, "password": password})
            st.sidebar.success("Controlla l'email!")
        except Exception as e:
            st.sidebar.error(f"Errore: {e}")

if not st.session_state['auth']:
    st.title("💠 Coin-Nexus Quantum AI")
    st.info("Benvenuto. Effettua il login per iniziare l'analisi.")
    login_supabase()
    st.stop()

# --- 4. APP PRINCIPALE ---
st.title(f"🚀 Dashboard di {st.session_state['user_email']}")
file = st.file_uploader("Carica Bilancio (Excel/CSV)", type=['xlsx', 'csv'])

if file:
    try:
        if file.name.endswith('.xlsx'):
            xl = pd.ExcelFile(file)
            sheet = st.selectbox("Seleziona Foglio", xl.sheet_names)
            df = xl.parse(sheet)
        else:
            df = pd.read_csv(file)

        st.divider()
        col_desc, col_val = st.columns(2)
        with col_desc:
            descr_col = st.selectbox("Colonna Descrizioni", df.columns)
        with col_val:
            num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if not num_cols:
                st.error("Nessuna colonna numerica trovata!")
                st.stop()
            val_col = st.selectbox("Colonna Valori (€)", num_cols)

        if st.button("📊 AVVIA ANALISI QUANTUM"):
            massa = df[val_col].abs().sum()
            mat = massa * 0.015
            
            # Grafici
            st.subheader("📈 Analisi Visiva")
            fig = px.pie(df.head(10), names=descr_col, values=val_col, title="Distribuzione Massa")
            st.plotly_chart(fig)

            # SALVATAGGIO SU SUPABASE (Assicurati che la tabella esista!)
            try:
                log_data = {
                    "user_email": st.session_state['user_email'],
                    "massa": float(massa),
                    "materialita": float(mat)
                }
                supabase.table("analisi_bilanci").insert(log_data).execute()
                st.success("✅ Analisi salvata nel Cloud Supabase")
            except Exception as e:
                st.warning(f"Salvataggio cloud non riuscito: {e}")

    except Exception as e:
        st.error(f"Errore tecnico: {e}")
