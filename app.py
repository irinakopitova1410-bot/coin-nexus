import streamlit as st
import requests
import time
import pandas as pd
from supabase import create_client

# 1. Configurazione Iniziale e Sidebar
st.set_page_config(page_title="Nexus Finance AI", layout="wide")
st.sidebar.title("Configurazione")

# Recupero segreti da Streamlit Cloud
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("Configura i Secrets (SUPABASE_URL e SUPABASE_KEY) su Streamlit Cloud!")

# URL del tuo Backend su Render
API_URL = "https://nexus-api-rf76.onrender.com/v1/analyze"
API_KEY = "nx-live-docfinance-2026"

st.title("🏛️ Nexus Finance AI - Analisi Rischio Pro")
st.markdown("Carica il bilancio aziendale in formato Excel per calcolare lo Z-Score e l'affidabilità con AI.")

# 2. Caricamento File
nome_azienda = st.text_input("Nome dell'Azienda da analizzare", placeholder="Es. DocFinance S.p.A.")
uploaded_file = st.file_uploader("Scegli un file Excel (.xlsx)", type=["xlsx"])

if uploaded_file and nome_azienda:
    try:
        # Legge l'excel
        df = pd.read_excel(uploaded_file)
        st.write("### Anteprima Dati")
        st.dataframe(df.head(5))
        
        # Converte il DataFrame in una lista di dizionari per l'invio JSON
        dati_da_inviare = df.to_dict(orient="records")
        
        if st.button("🚀 Avvia Analisi Predittiva"):
            payload = {
                "azienda": nome_azienda,
                "records": dati_da_inviare
            }
            headers = {"x-api-key": API_KEY}
            
            # 3. Invio al Backend su Render
            with st.status("Invio dati al server Nexus AI...", expanded=True) as status:
                try:
                    response = requests.post(API_URL, json=payload, headers=headers, timeout=20)
                    
                    if response.status_code == 200:
                        analysis_id = response.json().get("id")
                        status.update(label="✅ Dati ricevuti! Elaborazione AI in corso su Supabase...", state="running")
                        
                        # 4. Loop di controllo (Polling) su Supabase
                        completato = False
                        tentativi = 0
                        max_tentativi = 12 
                        
                        while not completato and tentativi < max_tentativi:
                            time.sleep(5) 
                            res = supabase.table("analisi_rischio").select("*").eq("id", analysis_id).execute()
                            
                            if res.data and res.data[0]['completato']:
                                status.update(label="✨ Analisi Completata!", state="complete")
                                st.balloons()
                                
                                # Visualizzazione Risultati
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric("Z-Score Finale", res.data[0]['z_score'])
                                with col2:
                                    st.subheader(f"Stato: {res.data[0]['stato_rischio']}")
                                
                                st.success(f"L'azienda **{nome_azienda}** è stata analizzata con successo.")
                                completato = True
                            
                            tentativi += 1
                        
                        if not completato:
                            st.warning("L'analisi sta richiedendo tempo. Controlla Supabase tra poco.")
                    
                    else:
                        st.error(f"Errore Server ({response.status_code}): {response.text}")
                
                except Exception as e:
                    st.error(f"Errore di connessione: {str(e)}")

    except Exception as e:
        st.error(f"Errore nella lettura del file: {e}")

st.sidebar.caption("Powered by Nexus AI Engine 202
