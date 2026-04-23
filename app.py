import streamlit as st
import requests
import pandas as pd

# 1. Configurazione URL (Assicurati che nei Secrets non ci sia lo slash finale)
BACKEND_URL = st.secrets.get("BACKEND_URL", "https://finance-analyzer-q9m8.onrender.com")

st.set_page_config(page_title="Nexus Finance", layout="wide")
st.title("🏛️ Nexus Finance Analyzer")

# --- SIDEBAR PER ACCESSO ---
with st.sidebar:
    st.header("Autenticazione")
    api_key = st.text_input("Inserisci API Key", type="password")

# --- CARICAMENTO DATI ---
uploaded_file = st.file_uploader("Carica file Excel o CSV", type=['xlsx', 'csv'])

if uploaded_file and api_key:
    # Lettura file
    if uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)
    
    st.write("### Anteprima Dati", df.head())

    # --- DEFINIZIONE COLONNE (IMPORTANTE!) ---
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚀 Analisi Score"):
            with st.spinner("Calcolo in corso..."):
                try:
                    res = requests.post(
                        f"{BACKEND_URL}/analyze-finance",
                        json={"data": df.to_dict(orient='records')},
                        headers={"x-api-key": api_key}
                    )
                    if res.status_code == 200:
                        st.success("Analisi completata!")
                        st.json(res.json())
                    else:
                        st.error(f"Errore {res.status_code}: {res.text}")
                except Exception as e:
                    st.error(f"Connessione fallita: {e}")

    with col2:
        if st.button("☁️ Push to Cloud"):
            with st.spinner("Salvataggio..."):
                try:
                    res = requests.post(
                        f"{BACKEND_URL}/save-to-supabase",
                        json={"data": df.to_dict(orient='records')},
                        headers={"x-api-key": api_key}
                    )
                    if res.status_code == 200:
                        st.balloons()
                        st.success("Dati salvati con successo!")
                        st.json(res.json())
                    else:
                        st.error(f"Errore {res.status_code}: {res.text}")
                except Exception as e:
                    st.error(f"Connessione fallita: {e}")
else:
    st.info("💡 Carica un file e inserisci l'API Key per attivare l'analisi.")
