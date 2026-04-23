import streamlit as st
import requests
import time
import pandas as pd
from supabase import create_client

st.set_page_config(page_title="Nexus Pro AI", layout="wide")

# Connessione Supabase
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
API_URL = "https://finance-analyzer-q9m8.onrender.com/v1/analyze"

st.title("📊 Nexus Finance - Business Intelligence AI")

azienda = st.text_input("Ragione Sociale")
file = st.file_uploader("Carica Bilancio (Excel)", type=["xlsx"])

if file and azienda:
    df = pd.read_excel(file)
    st.dataframe(df.head()) # Anteprima dati
    
    if st.button("ESEGUI ANALISI COMPLETA"):
        headers = {"x-api-key": "nx-live-docfinance-2026"}
        payload = {"azienda": azienda, "records": df.to_dict(orient="records")}
        
        with st.spinner("L'IA sta calcolando EBITDA, Z-Score e Proiezioni..."):
            resp = requests.post(API_URL, json=payload, headers=headers)
            if resp.status_code == 200:
                aid = resp.json()["id"]
                # Polling Supabase
                for _ in range(20):
                    time.sleep(3)
                    res = supabase.table("analisi_rischio").select("*").eq("id", aid).execute()
                    if res.data and res.data[0]['completato']:
                        data = res.data[0]
                        st.balloons()
                        
                        # Dashboard Risultati
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Z-Score", data['z_score'])
                        col2.metric("EBITDA", f"€ {data['ebitda']:,.2f}")
                        col3.success(f"Stato: {data['stato_rischio']}")
                        
                        st.subheader("📈 Proiezione Fatturato 4 Anni (AI Forecast)")
                        st.line_chart(data['proiezioni'])
                        break
            else:
                st.error("Errore di comunicazione con il server.")
