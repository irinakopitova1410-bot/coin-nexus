import streamlit as st
import pandas as pd
import requests
from supabase import create_client, Client
import datetime
import io

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Nexus Enterprise | SaaS Hub", layout="wide", page_icon="🏛️")

# --- 2. CONNESSIONE SUPABASE (SICURA) ---
@st.cache_resource
def init_supabase():
    try:
        # Legge dai Secrets di Streamlit Cloud (da impostare nella dashboard)
        url = st.secrets["https://ipmttldwfsxuubugiyir.supabase.co"]
        key = st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlwbXR0bGR3ZnN4dXVidWdpeWlyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjA5NDE3MSwiZXhwIjoyMDkxNjcwMTcxfQ.hFsH0_JtDOTgsPUm-RhvcZRztXqQmafaHgfMN6WxcKk"]
        return create_client(url, key)
    except Exception as e:
        return None

supabase = init_supabase()

# --- 3. LOGICA DI AUTENTICAZIONE ---
def login_logic(email_input, pwd_input):
    # BACKDOOR ADMIN
    ADMIN_MAIL = "admin@test.it" 
    ADMIN_PASS = "nexus2026"

    if email_input == ADMIN_MAIL and pwd_input == ADMIN_PASS:
        return {"email": ADMIN_MAIL, "role": "admin"}
    
    # LOGIN TRAMITE SUPABASE AUTH
    if supabase:
        try:
            res = supabase.auth.sign_in_with_password({"email": email_input, "password": pwd_input})
            if res:
                return {"email": res.user.email, "role": "user"}
        except:
            return None
    return None

# --- 4. GESTIONE SESSIONE ---
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
            st.success(f"Benvenuto {user_data['email']}!")
            st.rerun()
        else:
            st.error("Credenziali non valide.")
    st.stop()

# --- 5. SIDEBAR ---
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
    assets_in = st.number_input("Totale Attivo (€)", value=2000000.0)
    income_in = st.number_input("Utile Netto (€)", value=250000.0)

# --- 6. DASHBOARD PRINCIPALE ---
st.title("🕵️ Credit Risk & Enterprise Intelligence")

# --- INTEGRAZIONE REALE CON RENDER ---
if st.session_state.auth_user['role'] == "admin":
    st.divider()
    st.header("🔌 Doc-Finance Enterprise Integration")
    
    # URL del tuo server FastAPI su Render
    url_render = "https://nexus-api-rf76.onrender.com/analyze"
    
    col_api, col_log = st.columns([1.5, 1])

    with col_api:
        st.subheader("📡 Nexus Engine Live")
        st.info(f"Connesso al backend: {url_render}")
        
        # Anteprima JSON per la demo
        payload = {
            "company_name": nome_az,
            "revenue": rev_in,
            "total_assets": assets_in,
            "net_income": income_in
        }
        
        st.code(payload, language="json")
        
        if st.button("🚀 PUSH TO DOC-FINANCE (Render)", use_container_width=True):
            # API KEY che hai salvato nella tabella 'tenants' di Supabase
            headers = {"x-api-key": "nx-live-docfinance-2026"}
            
            with st.spinner("L'algoritmo sta calcolando su Render..."):
                try:
                    response = requests.post(url_render, json=payload, headers=headers)
                    if response.status_code == 200:
                        st.success("✅ RISPOSTA RICEVUTA DAL MOTORE!")
                        res = response.json()
                        
                        # Visualizzazione Risultati Real-time
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Z-Score", res['z_score'])
                        c2.metric("Rischio", res['risk_level'])
                        c3.metric("Saldo Crediti", res['remaining_credits'])
                        st.balloons()
                    else:
                        st.error(f"Errore {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"Server Offline o URL errato: {e}")

    with col_log:
        st.subheader("📊 Partner Dashboard")
        if supabase:
            try:
                # Recupero crediti residui dal DB
                t_res = supabase.table("tenants").select("credit_balance").eq("api_key", "nx-live-docfinance-2026").execute()
                if t_res.data:
                    saldo = t_res.data[0]['credit_balance']
                    st.metric("Crediti Disponibili", f"{saldo} / 5000")
                
                # Ultime 3 analisi registrate
                st.write("Ultime attività:")
                l_res = supabase.table("analysis_logs").select("company_name, z_score, created_at").order("created_at", desc=True).limit(3).execute()
                if l_res.data:
                    st.dataframe(pd.DataFrame(l_res.data), use_container_width=True)
            except:
                st.write("In attesa di dati...")
