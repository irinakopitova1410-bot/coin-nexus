import streamlit as st
import requests
import time
import pandas as pd
from supabase import create_client

st.set_page_config(page_title="Nexus Pro AI", layout="wide")

# Connessione Supabase
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except:
    st.error("Configura i Secrets su Streamlit Cloud!")

API_URL = "https://finance-analyzer-q9m8.onrender.com/v1/analyze"
API_KEY = "nx-live-docfinance-2026"

st.title("🏛️ Nexus Finance AI")

# Input
azienda = st.text_input("Ragione Sociale Azienda")
uploaded_file = st.file_uploader("Carica Bilancio Excel", type=["xlsx"])

if uploaded_file:
    # Mostra subito i dati caricati
    df = pd.read_excel(uploaded_file)
    st.write("✅ File caricato. Righe trovate:", len(df))
    
    if not azienda:
        st.warning("⚠️ Inserisci il nome dell'azienda per sbloccare l'analisi.")
    else:
        if st.button("🚀 AVVIA ANALISI ORA"):
            payload = {
                "azienda": azienda, 
                "records": df.to_dict(orient="records")
            }
            headers = {"x-api-key": API_KEY}
            
            with st.spinner("Connessione al server Render in corso..."):
                try:
                    res = requests.post(API_URL, json=payload, headers=headers, timeout=30)
                    if res.status_code == 200:
                        analysis_id = res.json().get("id")
                        st.info(f"Analisi ID {analysis_id} avviata. Controllo risultati...")
                        
                        # Loop di controllo
                        placeholder = st.empty()
                        for _ in range(15):
                            time.sleep(5)
                            check = supabase.table("analisi_rischio").select("*").eq("id", analysis_id).execute()
                            if check.data and check.data[0].get('completato'):
                                d = check.data[0]
                                st.balloons()
                                st.success("Analisi Completata!")
                                st.metric("Z-Score", d['z_score'])
                                st.metric("EBITDA", f"€ {d['ebitda']:,.2f}")
                                if d['proiezioni']:
                                    st.line_chart(d['proiezioni'])
                                break
                            placeholder.text(f"Elaborazione in corso... ({_+1}/15)")
                    else:
                        st.error(f"Errore Server: {res.text}")
                except Exception as e:
                    st.error(f"Errore connessione: {e}")
