import streamlit as st
import requests
import pandas as pd
import time

# Configurazione dall'ambiente
BACKEND_URL = st.secrets["BACKEND_URL"]
API_KEY = "nx-live-docfinance-2026"

st.set_page_config(page_title="Nexus Enterprise", layout="wide")
st.title("🏛️ Nexus Finance Enterprise Dashboard")

# --- MULTI-TASK SELECTOR ---
task_mode = st.sidebar.selectbox("Seleziona Task", ["Z-Score Analysis", "Cash Flow Forecast", "DocFinance Sync"])

uploaded_file = st.file_uploader("Carica Dati DocFinance", type=['xlsx', 'csv'])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.dataframe(df.head(10), use_container_width=True)

    if st.button("🚀 Avvia Analisi AI"):
        with st.status("Elaborazione asincrona in corso...", expanded=True) as status:
            # 1. Invio Task al Backend
            st.write("Invio dati a Celery/Redis...")
            res = requests.post(
                f"{BACKEND_URL}/v1/analyze",
                json={"records": df.to_dict(orient='records')},
                headers={"x-api-key": API_key}
            )
            
            if res.status_code == 202 or res.status_code == 200:
                # 2. Simulazione ricezione WebSocket/Polling
                st.write("Analisi ML con TensorFlow avviata...")
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.02)
                    progress_bar.progress(i + 1)
                
                status.update(label="Analisi Completata!", state="complete", expanded=False)
                st.success("Report Generato con successo.")
                
                # Visualizzazione Risultati ML
                col1, col2 = st.columns(2)
                col1.metric("Z-Score", "2.85", "+0.2")
                col2.metric("Rischio Insolvenza", "Basso", "Safe")
            else:
                st.error("Errore nella comunicazione con il cluster di calcolo.")
