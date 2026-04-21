import streamlit as st
import pandas as pd
import requests
from supabase import create_client, Client
import datetime

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Nexus Enterprise | SaaS Hub", layout="wide", page_icon="🏛️")

# --- 2. CONNESSIONE SUPABASE (SICURA) ---
@st.cache_resource
def init_supabase():
    try:
        # Legge dai Secrets di Streamlit Cloud (Configurali nelle impostazioni di Streamlit!)
        url = st.secrets["https://ipmttldwfsxuubugiyir.supabase.co"]
        key = st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlwbXR0bGR3ZnN4dXVidWdpeWlyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYwOTQxNzEsImV4cCI6MjA5MTY3MDE3MX0.HRFDqEKVCygVSKByVupgK3XGIkkpxxCyO7PH4LucPZg"]
        return create_client(url, key)
    except Exception as e:
        return None

supabase = init_supabase()

# --- 3. LOGICA DI AUTENTICAZIONE ---
def login_logic(email_input, pwd_input):
    ADMIN_MAIL = "admin@test.it" 
    ADMIN_PASS = "nexus2026"
    if email_input == ADMIN_MAIL and pwd_input == ADMIN_PASS:
        return {"email": ADMIN_MAIL, "role": "admin"}
    if supabase:
        try:
            res = supabase.auth.sign_in_with_password({"email": email_input, "password": pwd_input})
            if res:
                return {"email": res.user.email, "role": "user"}
        except:
            return None
    return None

if 'auth_user' not in st.session_state:
    st.session_state.auth_user = None

if st.session_state.auth_user is None:
    st.title("🏛️ Nexus Enterprise | Login")
    email = st.text_input("Email")
    pwd = st.text_input("Password", type="password")
    if st.button("Accedi al Sistema", use_container_width=True):
        user_data = login_logic(email, pwd)
        if user_data:
            st.session_state.auth_user = user_data
            st.rerun()
        else:
            st.error("Credenziali non valide.")
    st.stop()

# --- 4. SIDEBAR E INPUT ---
with st.sidebar:
    st.title("🏛️ Nexus System")
    st.write(f"👤 **Utente:** {st.session_state.auth_user['email']}")
    if st.button("Logout"):
        st.session_state.auth_user = None
        st.rerun()
    st.divider()
    st.subheader("Dati Analisi")
    nome_az = st.text_input("Ragione Sociale", "Target S.p.A.")
    rev_in = st.number_input("Fatturato (€)", value=1500000.0)
    ebit_in = st.number_input("EBITDA (€)", value=250000.0)
    pfn_in = st.number_input("Debito Totale (€)", value=500000.0)

# --- 5. DASHBOARD PRINCIPALE ---
st.title("🕵️ Credit Risk & Enterprise Intelligence")

if st.session_state.auth_user['role'] == "admin":
    st.divider()
    st.header("🔌 Doc-Finance Enterprise Integration")
    
    # URL del tuo server su Render
    url_render = "https://nexus-api-rf76.onrender.com/v1/scoring/analyze"
    
    col_api, col_log = st.columns([1.5, 1])

    with col_api:
        st.subheader("📡 Nexus Engine Live")
        st.info(f"Endpoint: {url_render}")
        
        # Payload coordinato con ScoringRequest in main.py
        payload = {
            "company_name": nome_az,
            "revenue": float(rev_in),
            "ebitda": float(ebit_in),
            "total_debt": float(pfn_in)
        }
        
        st.code(payload, language="json")
        
        if st.button("🚀 PUSH TO DOC-FINANCE (Render)", use_container_width=True):
            headers = {"x-api-key": "nx-live-docfinance-2026"}
            with st.spinner("L'algoritmo sta calcolando su Render..."):
                try:
                    response = requests.post(url_render, json=payload, headers=headers)
                    if response.status_code == 200:
                        st.success("✅ ANALISI COMPLETATA!")
                        res = response.json()
                        # Mostra i risultati che arrivano dal server
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Z-Score", res['results']['score'])
                        c2.metric("Rating", res['results']['rating'])
                        c3.metric("Crediti Residui", res['results']['credits_left'])
                        st.balloons()
                    else:
                        st.error(f"Errore {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"Connessione fallita. Verifica che Render sia LIVE.")

    with col_log:
        st.subheader("📊 Partner Dashboard")
        if supabase:
            try:
                # Recupero saldo crediti reale
                t_res = supabase.table("tenants").select("credit_balance").eq("api_key", "nx-live-docfinance-2026").execute()
                if t_res.data:
                    st.metric("Saldo DocFinance", f"{t_res.data[0]['credit_balance']} / 5000")
                
                # Tabella log
                st.write("Ultime operazioni:")
                l_res = supabase.table("analysis_logs").select("company_name, z_score, created_at").order("created_at", desc=True).limit(5).execute()
                if l_res.data:
                    st.dataframe(pd.DataFrame(l_res.data), use_container_width=True)
            except:
                st.write("In attesa di dati dal database...")
