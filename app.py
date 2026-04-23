import streamlit as st
import requests
import time
import pandas as pd
from supabase import create_client

# Configurazione Dashboard
st.set_page_config(page_title="Nexus Pro Dashboard", layout="wide", page_icon="🏛️")

# Inizializzazione Database
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except:
    st.error("Errore: Configura SUPABASE_URL e SUPABASE_KEY nei Secrets!")

API_URL = "https://finance-analyzer-q9m8.onrender.com/v1/analyze"
API_KEY = "nx-live-docfinance-2026"

st.title("🏛️ Nexus Finance - Intelligence Dashboard")
st.markdown("### Analisi Predittiva e Valutazione Rischio Aziendale")

# Layout Input
with st.container():
    col1, col2 = st.columns([1, 2])
    with col1:
        azienda = st.text_input("Ragione Sociale Azienda", placeholder="Es. DocFinance S.p.A.")
    with col2:
        file = st.file_uploader("Carica Bilancio Excel (.xlsx)", type=["xlsx"])

if file and azienda:
    df = pd.read_excel(file)
    st.info(f"✅ {len(df)} righe caricate. Pronto per l'elaborazione.")
    
    if st.button("🚀 AVVIA ANALISI COMPLETA"):
        headers = {"x-api-key": API_KEY}
        payload = {"azienda": azienda, "records": df.to_dict(orient="records")}
        
        with st.status("📡 Comunicazione con il motore AI...", expanded=True) as status:
            try:
                # Chiamata al Backend
                response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    analysis_id = response.json()["id"]
                    status.update(label="⚙️ Elaborazione indicatori avanzati...", state="running")
                    
                    # Polling per i risultati
                    for i in range(20):
                        time.sleep(4)
                        res = supabase.table("analisi_rischio").select("*").eq("id", analysis_id).execute()
                        
                        if res.data and res.data[0].get('completato'):
                            d = res.data[0]
                            status.update(label="✨ Analisi completata!", state="complete")
                            st.balloons()
                            
                            # --- VISUALIZZAZIONE RISULTATI ---
                            st.divider()
                            k1, k2, k3, k4 = st.columns(4)
                            k1.metric("Altman Z-Score", d['z_score'])
                            k2.metric("EBITDA", f"€ {d['ebitda']:,.0f}")
                            k3.metric("Margine EBITDA", f"{d.get('ebitda_margin', 0)}%")
                            k4.info(f"Rating: {d['stato_rischio']}")
                            
                            st.subheader("📈 Trend Proiettato (Prossimi 4 Anni)")
                            st.area_chart(d['proiezioni'])
                            break
                else:
                    st.error(f"Errore Server: {response.status_code}")
            except Exception as e:
                st.error(f"Errore connessione: {str(e)}")

st.sidebar.caption("Nexus AI v2.0 - 2026")
