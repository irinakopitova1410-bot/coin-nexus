import streamlit as st
import requests
import time
import pandas as pd
from supabase import create_client

st.set_page_config(page_title="Nexus Finance Pro", layout="wide")

# Credenziali
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
API_URL = "https://finance-analyzer-q9m8.onrender.com/v1/analyze"

st.title("🏛️ Nexus Finance - Intelligence Dashboard")

# UI di Input
col_in1, col_in2 = st.columns([1, 2])
with col_in1:
    azienda = st.text_input("Ragione Sociale")
with col_in2:
    file = st.file_uploader("Carica Excel Bilancio", type=["xlsx"])

if file and azienda:
    df = pd.read_excel(file)
    st.success(f"Dati caricati: {len(df)} righe.")

    if st.button("🔥 GENERA REPORT AUDACE"):
        headers = {"x-api-key": "nx-live-docfinance-2026"}
        payload = {"azienda": azienda, "records": df.to_dict(orient="records")}
        
        with st.status("🚀 Motore Nexus AI in azione...", expanded=True) as status:
            try:
                res = requests.post(API_URL, json=payload, headers=headers, timeout=30)
                if res.status_code == 200:
                    analysis_id = res.json()["id"]
                    
                    # Polling Risultati
                    for i in range(12):
                        time.sleep(5)
                        db_res = supabase.table("analisi_rischio").select("*").eq("id", analysis_id).execute()
                        if db_res.data and db_res.data[0]['completato']:
                            d = db_res.data[0]
                            status.update(label="✅ Analisi Completata!", state="complete")
                            st.balloons()
                            
                            # --- VISUALIZZAZIONE KPI ---
                            st.divider()
                            k1, k2, k3 = st.columns(3)
                            k1.metric("ALTMAN Z-SCORE", d['z_score'], delta="Rischio Calcolato")
                            k2.metric("EBITDA ATTUALE", f"€ {d['ebitda']:,.2f}")
                            k3.metric("RATING", d['stato_rischio'])
                            
                            # --- GRAFICO PROIEZIONI ---
                            st.subheader("📈 Proiezione Trend Fatturato (4 Anni)")
                            st.area_chart(d['proiezioni'])
                            
                            st.info(f"L'analisi per {azienda} è stata salvata nel database Supabase.")
                            break
                else:
                    st.error(f"Errore: {res.status_code}")
            except Exception as e:
                st.error(f"Connessione fallita: {e}")
