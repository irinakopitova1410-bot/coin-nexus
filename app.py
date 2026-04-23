import streamlit as st
import requests
import pandas as pd

# CONFIGURAZIONE - Prende l'URL dai Secrets di Streamlit
BACKEND_URL = st.secrets.get("BACKEND_URL", "https://finance-analyzer-q9m8.onrender.com")

st.set_page_config(page_title="Nexus Analyzer", layout="wide")
st.title("🏛️ Nexus Finance Analyzer")

# Sidebar per Key
with st.sidebar:
    api_key = st.text_input("Inserisci API Key", type="password")

# Caricamento File
file = st.file_uploader("Carica Excel", type=['xlsx', 'csv'])

if file and api_key:
    df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
    st.dataframe(df.head())

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚀 Analisi Score"):
            # CHIAMATA AL BACKEND
            res = requests.post(
                f"{BACKEND_URL}/analyze-finance", 
                json={"data": df.to_dict(orient='records')},
                headers={"x-api-key": api_key}
            )
            if res.status_code == 200:
                st.success("Analisi Completata!")
                st.json(res.json())
            else:
                st.error(f"Errore {res.status_code}: {res.text}")

    with col2:
        if st.button("☁️ Push to Cloud"):
            # CHIAMATA AL BACKEND
            res = requests.post(
                f"{BACKEND_URL}/save-to-supabase",
                json={"data": df.to_dict(orient='records')},
                headers={"x-api-key": api_key}
            )
            if res.status_code == 200:
                st.balloons()
                st.success("Dati salvati!")
            else:
                st.error(f"Errore {res.status_code}: {res.text}")
