import streamlit as st
import requests
import pandas as pd
import numpy as np

# Configurazione URL dai Secrets (Assicurati che non ci sia lo slash / finale)
BACKEND_URL = st.secrets.get("BACKEND_URL", "https://finance-analyzer-q9m8.onrender.com")

st.set_page_config(page_title="Nexus Multi-Task Analyzer", layout="wide")

# --- STILE E TITOLO ---
st.title("🏛️ Nexus Finance Multi-Task System")
st.markdown("---")

# --- SIDEBAR: GESTIONE ACCESSO ---
with st.sidebar:
    st.header("🔐 Autenticazione")
    api_key = st.text_input("Inserisci API Key Enterprise", type="password")
    if api_key == "nx-live-docfinance-2026":
        st.success("Accesso Autorizzato")
    elif api_key:
        st.error("Chiave non valida")

# --- CARICAMENTO DATI ---
st.subheader("1️⃣ Caricamento Dati ERP / DocFinance")
uploaded_file = st.file_uploader("Trascina qui il file Excel o CSV", type=['xlsx', 'csv'])

if uploaded_file and api_key == "nx-live-docfinance-2026":
    # Lettura flessibile del file
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    
    st.write("### Anteprima Flussi Caricati", df.head(5))
    
    st.markdown("---")
    st.subheader("2️⃣ Pannello di Controllo Multi-Task")
    
    # Creazione di 3 colonne per le diverse funzioni
    col1, col2, col3 = st.columns(3)

    # --- TASK 1: CALCOLO RISCHIO (Z-SCORE) ---
    with col1:
        st.info("📊 **Analisi Rischio**")
        if st.button("Calcola Z-Score"):
            with st.spinner("Analizzando indici di bilancio..."):
                try:
                    # Chiamata al backend per il calcolo complesso
                    res = requests.post(
                        f"{BACKEND_URL}/analyze-finance",
                        json={"data": df.to_dict(orient='records')},
                        headers={"x-api-key": api_key}
                    )
                    if res.status_code == 200:
                        data = res.json()
                        score = data.get('score', 0)
                        rating = data.get('rating', 'N/D')
                        
                        st.metric("Financial Health Score", f"{score:.2f}")
                        if score > 2.6:
                            st.success(f"Rating: {rating} (Sicuro)")
                        elif score > 1.1:
                            st.warning(f"Rating: {rating} (Attenzione)")
                        else:
                            st.error(f"Rating: {rating} (Rischio Fallimento)")
                    else:
                        st.error("Errore nel calcolo del rischio.")
                except Exception as e:
                    st.error(f"Connessione fallita: {e}")

    # --- TASK 2: PUSH TO CLOUD (SUPABASE) ---
    with col2:
        st.info("☁️ **Archiviazione**")
        if st.button("Salva su Supabase"):
            with st.spinner("Sincronizzazione Cloud..."):
                try:
                    res = requests.post(
                        f"{BACKEND_URL}/save-to-supabase",
                        json={"data": df.to_dict(orient='records')},
                        headers={"x-api-key": api_key}
                    )
                    if res.status_code == 200:
                        st.balloons()
                        st.success("✅ Backup completato!")
                    else:
                        st.error(f"Errore salvataggio: {res.status_code}")
                except Exception as e:
                    st.error(f"Errore cloud: {e}")

    # --- TASK 3: EXPORT REPORT ---
    with col3:
        st.info("📑 **Reportistica**")
        if st.button("Genera Report PDF"):
            st.write("Generazione report in corso...")
            # Qui potresti aggiungere la logica per scaricare un PDF o un riepilogo
            st.warning("Funzione Export in fase di attivazione.")

else:
    if not api_key:
        st.warning("⚠️ Inserisci l'API Key nella sidebar per sbloccare le funzioni.")
    elif not uploaded_file:
        st.info("📂 Carica un file per iniziare l'analisi multi-task.")
