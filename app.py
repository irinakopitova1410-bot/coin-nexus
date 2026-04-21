import streamlit as st
import requests
import pandas as pd
from io import BytesIO

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Nexus Fintech Platform", layout="wide")

# --- SIMULAZIONE MULTI-TENANT (LOGIN) ---
with st.sidebar:
    st.title("🔐 Accesso Partner")
    api_key_input = st.text_input("Inserisci la tua API Key Enterprise", value="nexus_test_key_2026", type="password")
    st.divider()

# --- INPUT DATI ---
st.title("🏛️ Nexus Engine | Fintech Dashboard")
nome_az = st.text_input("Ragione Sociale Cliente", "Azienda Beta S.p.A.")

col_in1, col_in2, col_in3 = st.columns(3)
with col_in1: rev = st.number_input("Fatturato (€)", 1500000.0)
with col_in2: ebit = st.number_input("EBITDA (€)", 250000.0)
with col_in3: pfn = st.number_input("PFN (Debito) (€)", 400000.0)

# Calcolo locale rapido
z = (1.2 * (rev * 0.1 / (pfn if pfn > 0 else 1))) + (3.3 * (ebit / (pfn if pfn > 0 else 1)))

# --- EXPORT ERP & SCARICA DATI ---
st.subheader("📥 Export ERP & Reporting")
col_down1, col_down2, col_down3 = st.columns(3)

# Prepariamo i dati per l'export
df_erp = pd.DataFrame([{
    "ID_CLIENTE": nome_az,
    "FATTURATO": rev,
    "EBITDA": ebit,
    "PFN": pfn,
    "Z_SCORE": round(z, 2),
    "DATA": "2026-04-21"
}])

with col_down1:
    csv = df_erp.to_csv(index=False).encode('utf-8')
    st.download_button("📑 Scarica Tracciato ERP (CSV)", csv, f"erp_export_{nome_az}.csv", "text/csv")

with col_down2:
    # Simulazione integrazione SAP/Doc-Finance
    if st.button("📤 Invia a Gestionale (ERP)"):
        st.success(f"Dati di {nome_az} inviati al webservice ERP con successo!")

with col_down3:
    st.info("💎 Piano: PRO (Illimitato)")

# --- INTEGRAZIONE RENDER (IL CUORE DEL SISTEMA) ---
st.divider()
if st.button("🚀 PUSH TO CLOUD & SYNC DB"):
    url = "https://nexus-api-rf76.onrender.com/v1/scoring/analyze"
    headers = {"x-api-key": api_key_input}
    payload = {"company_name": nome_az, "revenue": rev, "ebitda": ebit, "total_debt": pfn}
    
    with st.spinner("Sincronizzazione crittografata in corso..."):
        try:
            r = requests.post(url, json=payload, headers=headers)
            if r.status_code == 200:
                res = r.json()
                st.balloons()
                st.success(f"Analisi salvata! Crediti residui: {res['results']['credits_left']}")
            else:
                st.error(f"Errore: {r.text}")
        except Exception as e:
            st.error(f"Connessione fallita: {e}")
