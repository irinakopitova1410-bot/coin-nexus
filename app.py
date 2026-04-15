import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. SETUP CHIAVI SUPABASE (DA SETTINGS STREAMLIT) ---
# Se non hai ancora configurato i Secrets, l'app userà la modalità Demo
try:
    from supabase import create_client, Client
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
    db_status = "✅ Cloud Connected"
except Exception as e:
    supabase = None
    db_status = "⚠️ Demo Mode (No DB)"

# --- 2. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Coin-Nexus Enterprise", layout="wide")

# --- 3. LOGICA DI ACCESSO ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🏛️ Coin-Nexus | Secure Access")
    st.write("Inserire le credenziali Master per sbloccare il terminale.")
    
    with st.container():
        u = st.text_input("Admin Email", placeholder="admin@coin-nexus.com")
        p = st.text_input("Quantum Key", type="password", placeholder="quantum2026")
        
        if st.button("SBLOCCA TERMINALE"):
            if u == "admin@coin-nexus.com" and p == "quantum2026":
                st.session_state['auth'] = True
                st.rerun()
            else:
                st.error("Accesso negato. Credenziali non valide.")
    st.stop()

# --- 4. DASHBOARD (VISIBILE SOLO DOPO LOGIN) ---
st.title("🚀 Terminale Strategico Coin-Nexus")
st.sidebar.success(db_status)

if st.sidebar.button("LOGOUT"):
    st.session_state['auth'] = False
    st.rerun()

# Layout KPI
c1, c2, c3 = st.columns(3)
c1.metric("Rating Basilea IV", "AAA")
c2.metric("Compliance", "ISA 320")
c3.metric("Status", "Audit Ready")

st.divider()

st.subheader("📊 Analisi e Flussi")
up = st.file_uploader("Trascina qui il file ERP/CBI", type=['csv', 'xlsx'])

if up:
    st.success("File ricevuto. Elaborazione algoritmi di materialità...")
    # Qui inseriremo i grafici Plotly una volta che l'app è online
