import streamlit as st
import requests
import pandas as pd
from supabase import create_client, Client

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Nexus - AI Financial Scoring", layout="wide")

# --- CONNESSIONE SUPABASE ---
@st.cache_resource
def init_supabase():
    try:
        # Legge dai Secrets di Streamlit (Configurali nella Dashboard di Streamlit!)
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        return None

supabase_client = init_supabase()

# --- AUTENTICAZIONE ---
if 'auth_user' not in st.session_state:
    st.session_state.auth_user = None

if not st.session_state.auth_user:
    st.title("🔐 Login Nexus")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Accedi"):
        if user == "admin@test.it" and pwd == "nexus2026":
            st.session_state.auth_user = {"role": "admin", "name": "Doc Finance Admin"}
            st.rerun()
        else:
            st.error("Credenziali errate")
    st.stop()

# --- INTERFACCIA PRINCIPALE ---
st.title("🏦 Nexus - Motore di Analisi Credito")
st.sidebar.write(f"Connesso come: **{st.session_state.auth_user['name']}**")
if st.sidebar.button("Logout"):
    st.session_state.auth_user = None
    st.rerun()

# --- SEZIONE ANALISI ---
st.subheader("🚀 Nuova Analisi Società")
col1, col2 = st.columns(2)

with col1:
    company = st.text_input("Ragione Sociale")
    revenue = st.number_input("Fatturato (€)", min_value=0.0)
with col2:
    assets = st.number_input("Totale Attivo (€)", min_value=0.0)
    income = st.number_input("Utile Netto (€)", min_value=0.0)

if st.button("Esegui Analisi API"):
    if company and revenue > 0:
        with st.spinner("Interrogazione motore Nexus in corso..."):
            try:
                # 🚨 ATTENZIONE: Controlla che questo URL sia quello corretto su Render!
                API_URL = "https://nexus-api-m6r6.onrender.com/analyze"
                
                payload = {
                    "company_name": company,
                    "revenue": revenue,
                    "total_assets": assets,
                    "net_income": income
                }
                # Questa chiave deve essere la stessa nella tabella 'tenants' su Supabase
                headers = {"x-api-key": "nexus_test_key_2026"}
                
                response = requests.post(API_URL, json=payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("Analisi Completata!")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Z-Score", data['z_score'])
                    c2.metric("Rischio", data['risk_level'])
                    c3.metric("Crediti Residui", data['remaining_credits'])
                    st.balloons()
                else:
                    st.error(f"Errore API ({response.status_code}): {response.text}")
            except Exception as e:
                st.error(f"Impossibile connettersi al server Render: {e}")
    else:
        st.warning("Inserisci i dati societari per procedere.")

# --- DASHBOARD PARTNER (SOLO ADMIN) ---
if st.session_state.auth_user['role'] == "admin":
    st.divider()
    st.header("📊 Nexus Partner Dashboard")
    
    if supabase_client:
        try:
            # 1. Recupero Crediti
            t_res = supabase_client.table("tenants").select("name, credit_balance").eq("api_key", "nexus_test_key_2026").execute()
            
            if t_res.data:
                info = t_res.data[0]
                d1, d2 = st.columns(2)
                d1.metric("Partner Attivo", info['name'])
                d2.metric("Crediti Disponibili", f"{info['credit_balance']} / 5000")

            # 2. Storico Analisi
            st.subheader("📜 Ultimi Log di Integrazione")
            l_res = supabase_client.table("analysis_logs").select("created_at, company_name, z_score, pd_rate").order("created_at", desc=True).limit(5).execute()
            
            if l_res.data:
                df_logs = pd.DataFrame(l_res.data)
                df_logs.columns = ['Data', 'Azienda', 'Score', 'Rischio']
                st.dataframe(df_logs, use_container_width=True)
            else:
                st.info("Nessuna operazione registrata nel database.")
        except Exception as e:
            st.error(f"Errore database: {e}")
    else:
        st.warning("⚠️ Configurazione Supabase non trovata nei Secrets di Streamlit.")
