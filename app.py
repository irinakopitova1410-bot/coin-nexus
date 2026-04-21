import streamlit as st
import requests
import pandas as pd
from supabase import create_client, Client

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Nexus Enterprise", page_icon="🏛️", layout="wide")

# Inizializzazione Supabase per la Dashboard (Legge dai Secrets di Streamlit)
@st.cache_resource
def get_supabase():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except:
        return None

supabase = get_supabase()

# --- LOGIN ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🏛️ Nexus Enterprise Login")
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Entra"):
        if user == "admin@test.it" and pw == "nexus2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Credenziali errate")
    st.stop()

# --- DASHBOARD ---
st.title("🕵️ Nexus Risk Intelligence")

with st.sidebar:
    st.header("Parametri Analisi")
    azienda = st.text_input("Nome Azienda", "Esempio S.p.A.")
    fatturato = st.number_input("Fatturato (€)", value=1000000)
    ebitda = st.number_input("EBITDA (€)", value=150000)
    debito = st.number_input("Debito Totale (€)", value=300000)
    
    st.divider()
    if st.button("Logout"):
        st.session_state.auth = False
        st.rerun()

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🚀 Integrazione Doc-Finance")
    st.write("Invia i dati al motore di calcolo su Render per aggiornare il rating e scalare i crediti.")
    
    if st.button("PUSH TO DOC-FINANCE", use_container_width=True):
        # L'URL del tuo server su Render
        URL_RENDER = "https://nexus-api-rf76.onrender.com/v1/scoring/analyze"
        
        # Dati da inviare (devono corrispondere a ScoringRequest in main.py)
        payload = {
            "company_name": azienda,
            "revenue": float(fatturato),
            "ebitda": float(ebitda),
            "total_debt": float(debito)
        }
        
        # Header con la chiave che hai impostato su Render
        headers = {"x-api-key": "nx-live-docfinance-2026"}
        
        try:
            with st.spinner("Calcolo in corso su Render..."):
                res = requests.post(URL_RENDER, json=payload, headers=headers)
                
            if res.status_code == 200:
                data = res.json()
                st.success("✅ Analisi Completata e Credito Scalato!")
                
                # Mostra Risultati
                c1, c2, c3 = st.columns(3)
                c1.metric("Z-Score", data['results']['score'])
                c2.metric("Rating", data['results']['rating'])
                c3.metric("Crediti Residui", data['results']['credits_left'])
                st.balloons()
            else:
                st.error(f"Errore {res.status_code}: {res.text}")
        except Exception as e:
            st.error(f"Impossibile connettersi a Render: {e}")

with col2:
    st.subheader("📊 Stato Partner")
    if supabase:
        # Recupero saldo reale da Supabase per la visualizzazione
        try:
            res_db = supabase.table("tenants").select("credit_balance").eq("api_key", "nx-live-docfinance-2026").execute()
            if res_db.data:
                saldo = res_db.data[0]['credit_balance']
                st.metric("Saldo Crediti", f"{saldo} / 5000")
                st.progress(saldo / 5000)
        except:
            st.warning("Dati saldo non disponibili")
    
    st.write("**Ultimi Log:**")
    # Qui potresti aggiungere una tabella con gli ultimi log presi da Supabase
