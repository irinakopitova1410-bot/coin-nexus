import streamlit as st
import requests
import time
from supabase import create_client

# Configurazione Supabase per leggere i risultati
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("Nexus Finance AI - Analisi Pro")

# ... (parte del caricamento file Excel) ...

if st.button("Avvia Analisi AI"):
    payload = {
        "azienda": nome_azienda,
        "records": dati_da_inviare
    }
    
    headers = {"x-api-key": "nx-live-docfinance-2026"}
    
    # Invia al Backend Render
    response = requests.post("https://tua-api-render.com/v1/analyze", json=payload, headers=headers)
    
    if response.status_code == 200:
        analysis_id = response.json().get("id")
        st.success(f"Analisi avviata! ID: {analysis_id}")
        
        # Placeholder per il caricamento
        with st.spinner("L'intelligenza artificiale sta elaborando i dati su Supabase..."):
            completato = False
            tentativi = 0
            while not completato and tentativi < 10:
                time.sleep(5) # Aspetta 5 secondi prima di controllare
                # Controlla lo stato su Supabase
                res = supabase.table("analisi_rischio").select("*").eq("id", analysis_id).execute()
                if res.data and res.data[0]['completato']:
                    st.balloons()
                    st.write(f"### Risultato: {res.data[0]['stato_rischio']}")
                    st.write(f"**Z-Score:** {res.data[0]['z_score']}")
                    completato = True
                tentativi += 1
    else:
        st.error("Errore nell'invio dei dati al server.")
