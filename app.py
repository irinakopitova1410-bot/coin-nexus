import streamlit as st
import requests
import time
import pandas as pd
from supabase import create_client

# --- CONFIGURAZIONE DASHBOARD ---
st.set_page_config(page_title="Nexus Pro Dashboard", layout="wide", page_icon="🏛️")

# --- INIZIALIZZAZIONE DATABASE ---
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

try:
    supabase = init_supabase()
except Exception as e:
    st.error("Errore: Controlla i Secrets di Supabase!")

# CONFIGURAZIONE API RENDER
API_URL = "https://finance-analyzer-q9m8.onrender.com/v1/analyze"
API_KEY = "nx-live-docfinance-2026"

st.title("🏛️ Nexus Finance - Intelligence Dashboard")
st.markdown("### 🕵️ Analisi Predittiva e Prevenzione Fallimento")

# --- INPUT AREA ---
with st.container():
    col1, col2 = st.columns([1, 2])
    with col1:
        azienda = st.text_input("Ragione Sociale Azienda", placeholder="Es. DocFinance S.p.A.")
    with col2:
        file = st.file_uploader("Carica Bilancio Excel (.xlsx)", type=["xlsx"])

# --- LOGICA DI ANALISI ---
if file and azienda:
    df = pd.read_excel(file)
    st.info(f"✅ Dati caricati correttamente. Pronto per lo Stress Test.")
    
    if st.button("🚀 AVVIA ANALISI PREDITTIVA"):
        headers = {"x-api-key": API_KEY}
        payload = {"azienda": azienda, "records": df.to_dict(orient="records")}
        
        with st.status("📡 Comunicazione con il motore AI Quantum...", expanded=True) as status:
            try:
                response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    analysis_id = response.json()["id"]
                    status.update(label="⚙️ Calcolo Probabilità di Default (PD)...", state="running")
                    
                    # Polling per i risultati
                    for i in range(20):
                        time.sleep(3)
                        res = supabase.table("analisi_rischio").select("*").eq("id", analysis_id).execute()
                        
                        if res.data and res.data[0].get('completato'):
                            d = res.data[0]
                            status.update(label="✨ Analisi Predittiva Completata!", state="complete")
                            st.balloons()
                            
                            # --- VISUALIZZAZIONE RISULTATI (RIFATTA) ---
                            st.divider()
                            
                            # Indicatori Principali
                            k1, k2, k3, k4 = st.columns(4)
                            k1.metric("Altman Z-Score", d['z_score'])
                            k2.metric("EBITDA", f"€ {d['ebitda']:,.0f}")
                            
                            # Nuova metrica Probabilità di Fallimento
                            pd_value = d.get('pd', 0)
                            k3.metric(
                                "Probabilità Fallimento", 
                                f"{pd_value}%", 
                                delta="CRITICO" if pd_value > 50 else "STABILE",
                                delta_color="inverse"
                            )
                            k4.info(f"Stato: {d['stato_rischio']}")

                            # Box di Allerta Early Warning
                            if pd_value > 50:
                                st.error(f"⚠️ **ALLERTA CRISI**: {d.get('warning_level', 'Rischio elevato di insolvenza nei prossimi 12 mesi.')}")
                            else:
                                st.success(f"✅ **SICUREZZA**: {d.get('warning_level', 'L''azienda mostra una solida tenuta finanziaria.')}")

                            # Grafico Stress Test
                            st.subheader("📉 Stress Test: Proiezione Fatturato in caso di crisi (-10% annuo)")
                            st.area_chart(d['proiezioni'])
                            
                            # Storico Rapido
                            st.write("---")
                            st.caption("Nexus AI v2.0 - Motore di Prevenzione Crisi d'Impresa")
                            break
                else:
                    st.error(f"Errore Server: {response.status_code}")
            except Exception as e:
                st.error(f"Errore connessione: {str(e)}")

st.sidebar.markdown("---")
st.sidebar.write("👤 Admin Access Active")
