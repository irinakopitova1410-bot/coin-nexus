import streamlit as st
import requests
import pandas as pd
import os

# 1. Configurazione URL e API Key dai Secrets di Streamlit
# Assicurati di aver impostato BACKEND_URL nei Secrets di Streamlit senza lo slash finale
BACKEND_URL = st.secrets.get("BACKEND_URL", "https://finance-analyzer-q9m8.onrender.com")
DEFAULT_API_KEY = "nx-live-docfinance-2026"

st.set_page_config(page_title="Nexus Finance Analyzer", layout="wide")

st.title("🏛️ Nexus Finance Analyzer")
st.subheader("Analisi Z-Score e Integrazione ERP")

# --- SEZIONE ACCESSO ---
with st.sidebar:
    st.header("🔐 Accesso")
    user_api_key = st.text_input("Inserisci API Key", type="password")
    if not user_api_key:
        st.warning("Inserisci l'API Key per procedere.")
        st.stop()

# --- CARICAMENTO DATI ---
uploaded_file = st.file_uploader("Carica il file Excel o CSV (Tracciato NTS/DocFinance)", type=['csv', 'xlsx'])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    st.write("### Anteprima Dati", df.head())

    col1, col2 = st.columns(2)

    # --- TASTO ANALISI ---
    with col1:
        if st.button("🚀 Esegui Analisi Z-Score"):
            # Chiamata all'endpoint /analyze-finance (deve corrispondere al main.py)
            with st.spinner("Calcolo in corso..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/analyze-finance",
                        json={"data": df.to_dict(orient='records')},
                        headers={"x-api-key": user_api_key}
                    )
                    if response.status_code == 200:
                        res_data = response.json()
                        st.success(f"Analisi Completata! Rating: {res_data.get('rating', 'N/D')}")
                    else:
                        st.error(f"Errore Analisi: {response.text}")
                except Exception as e:
                    st.error(f"Errore di connessione: {e}")

    # --- TASTO PUSH TO CLOUD (Il punto critico) ---
    with col2:
        if st.button("☁️ PUSH TO CLOUD"):
            # Chiamata all'endpoint /save-to-supabase (deve corrispondere al main.py)
            with st.spinner("Salvataggio su Supabase..."):
                try:
                    payload = {
                        "tenant_id": "auto", # Il backend lo identificherà tramite API Key
                        "data": df.to_dict(orient='records')
                    }
                    response = requests.post(
                        f"{BACKEND_URL}/save-to-supabase",
                        json=payload,
                        headers={"x-api-key": user_api_key}
                    )
                    
                    if response.status_code == 200:
                        st.balloons()
                        st.success("✅ Dati salvati con successo nel Cloud!")
                    else:
                        # Se ricevi "Not Found", controlla che il main.py abbia @app.post("/save-to-supabase")
                        st.error(f"Errore: {response.text}")
                except Exception as e:
                    st.error(f"Errore di connessione: {e}")
