import streamlit as st
import requests
import pandas as pd
from supabase import create_client, Client
import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Nexus - AI Financial Scoring", layout="wide")

# --- CONNESSIONE SUPABASE ---
@st.cache_resource
def init_supabase():
    try:
        # Legge dai Secrets di Streamlit Cloud
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        return None

supabase_client = init_supabase()

# --- GESTIONE SESSIONE / LOGIN ---
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
st.title("🏦 Nexus - AI Financial Engine")
st.sidebar.write(f"Utente: **{st.session_state.auth_user['name']}**")
if st.sidebar.button("Logout"):
    st.session_state.auth_user = None
    st.rerun()

# --- SEZIONE INPUT ANALISI ---
st.subheader("🚀 Nuova Analisi Società")
c1, c2 = st.columns(2)

with c1:
    company_name = st.text_input("Ragione Sociale Azienda", placeholder="Es. Rossi S.p.A.")
    revenue = st.number_input("Fatturato (€)", min_value=0.0, format="%.2f")
with c2:
    assets = st.number_input("Totale Attivo (€)", min_value=0.0, format="%.2f")
    net_income = st.number_input("Utile Netto (€)", min_value=0.0, format="%.2f")

# --- INTEGRAZIONE DOC-FINANCE (SOLO PER ADMIN) ---
if st.session_state.auth_user['role'] == "admin":
    st.divider()
    st.header("🔌 Doc-Finance Enterprise Integration")
    
    # URL di Render (Assicurati che sia quello Live su Render)
    url_render = "https://nexus-api-rf76.onrender.com/analyze"
    
    col_api, col_log = st.columns([1.5, 1])

    with col_api:
        st.subheader("📡 Nexus Engine Live")
        st.info(f"Endpoint: {url_render}")
        
        # Simulazione payload per la demo
        st.code(f"""
        POST /analyze
        X-API-KEY: nx-live-docfinance-2026
        {{
            "company_name": "{company_name}",
            "revenue": {revenue},
            "total_assets": {assets},
            "net_income": {net_income}
        }}
        """, language="json")
        
        if st.button("🚀 PUSH TO DOC-FINANCE (Render)"):
            if company_name == "":
                st.warning("Inserisci il nome dell'azienda prima di inviare.")
            else:
                # La chiave API che hai messo su Supabase nella tabella tenants
                headers = {"x-api-key": "nx-live-docfinance-2026"}
                payload = {
                    "company_name": company_name,
                    "revenue": revenue,
                    "total_assets": assets,
                    "net_income": net_income
                }
                
                with st.spinner("L'algoritmo sta calcolando su Render..."):
                    try:
                        response = requests.post(url_render, json=payload, headers=headers)
                        if response.status_code == 200:
                            st.success("✅ ANALISI COMPLETATA CON SUCCESSO!")
                            res_data = response.json()
                            
                            # Visualizzazione Risultati
                            m1, m2, m3 = st.columns(3)
                            m1.metric("Z-Score", res_data['z_score'])
                            m2.metric("Rischio", res_data['risk_level'])
                            m3.metric("Crediti Residui", res_data['remaining_credits'])
                            st.balloons()
                        elif response.status_code == 404:
