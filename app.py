import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
from supabase import create_client, Client
import datetime
import io

# --- 1. CONFIGURAZIONE ---
st.set_page_config(page_title="Nexus Enterprise | SaaS Hub", layout="wide", page_icon="🏛️")

@st.cache_resource
def init_supabase():
    try:
        # Qui usiamo i NOMI delle variabili, NON i valori reali
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Errore configurazione Secrets: {e}")
        return None

supabase = init_supabase()

# --- 2. LOGICA DI AUTENTICAZIONE IBRIDA ---
def login_logic(email_input, pwd_input):
    # --- ADMIN PROVVISORIO (BACKDOOR) ---
    # Cambia queste due stringhe con la mail e pass che vuoi usare tu per i test
    ADMIN_MAIL = "admin@test.it" 
    ADMIN_PASS = "nexus2026"

    if email_input == ADMIN_MAIL and pwd_input == ADMIN_PASS:
        return {"email": ADMIN_MAIL, "role": "admin"}
    
    # --- LOGIN STANDARD TRAMITE SUPOBASE ---
    if supabase:
        try:
            res = supabase.auth.sign_in_with_password({"email": email_input, "password": pwd_input})
            if res:
                return {"email": res.user.email, "role": "user"}
        except:
            return None
    return None

# --- 3. MOTORE ANALISI ENTERPRISE ---
def run_enterprise_analysis(rev, ebitda, debt):
    rev = max(rev, 1)
    eb_val = max(ebitda, 1)
    db_val = max(debt, 1)
    z = (1.2 * (rev*0.1/db_val)) + (3.3 * (eb_val/db_val))
    pd_rate = max(0.005, min(0.99, 1 / (1 + (z**2.5)))) 
    ead = rev * 0.15 
    expected_loss = ead * pd_rate * 0.45 
    suggested_rate = (0.04 + pd_rate + 0.03) * 100 
    
    status = "SOLIDO" if z > 2.6 else "VULNERABILE" if z > 1.1 else "DISTRESSED"
    color = "#00CC66" if z > 2.6 else "#FFA500" if z > 1.1 else "#FF4B4B"
    
    return {
        "z": z, "status": status, "color": color, 
        "pd": pd_rate * 100, "el": expected_loss, "rate": suggested_rate,
        "ros": (eb_val/rev)*100, "lev": debt/eb_val
    }

# --- 4. SCHERMATA LOGIN ---
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

# --- 5. DASHBOARD POST-LOGIN ---
with st.sidebar:
    st.title("🏛️ Nexus System")
    st.write(f"👤 **Sessione:** {st.session_state.auth_user['email']}")
    
    if st.session_state.auth_user['role'] == "admin":
        st.success("⚡ MODO AMMINISTRATORE")
    
    if st.button("Logout"):
        st.session_state.auth_user = None
        st.rerun()
    
    st.divider()
    uploaded_file = st.file_uploader("📂 Carica Bilancio ERP", type=["xlsx", "csv"])
    nome_az = st.text_input("Azienda", "Target S.p.A.")
    rev_in = st.number_input("Fatturato (€)", value=1500000)
    ebit_in = st.number_input("EBITDA (€)", value=250000)
    pfn_in = st.number_input("Debito (€)", value=500000)

st.title("🕵️ Credit Risk & Enterprise Intelligence")
if st.button("🚀 PUSH TO DOC-FINANCE (Render)"):
            import requests
            # Allineamento perfetto: 12 spazi dal bordo sinistro
            url_render = "https://nexus-api-rf76.onrender.com/v1/scoring/analyze"
            headers = {"x-api-key": "nexus_test_key_2026"}
            
            payload = {
                "company_name": nome_az,
                "revenue": float(rev_in), 
                "ebitda": float(ebit_in), 
                "total_debt": float(pfn_in)
            }
            
            with st.spinner("L'algoritmo sta calcolando su Render..."):
                try:
                    response = requests.post(url_render, json=payload, headers=headers)
                    
                    if response.status_code == 200:
                        st.success("✅ RISPOSTA RICEVUTA DAL MOTORE!")
                        st.json(response.json()) 
                        st.balloons()
                    elif response.status_code == 500:
                        st.error("❌ Errore 500: Il server Render ha un problema di connessione a Supabase.")
                    elif response.status_code == 403:
                        st.error("❌ Errore 403: API Key non valida nel database.")
                    else:
                        st.error(f"Errore {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"Il server non risponde all'indirizzo: {url_render}")
