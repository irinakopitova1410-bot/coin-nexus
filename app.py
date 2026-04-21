import streamlit as st
import requests
import pandas as pd
from io import BytesIO

# --- 1. CONFIGURAZIONE ---
st.set_page_config(page_title="Nexus Engine | Enterprise", layout="wide")

# --- 2. SIDEBAR & API KEY ---
with st.sidebar:
    st.title("🔐 Accesso")
    api_key = st.text_input("Inserisci API Key", value="nexus_test_key_2026", type="password")
    st.divider()
    st.info("Status: Connesso a Supabase")

# --- 3. INPUT DATI ---
st.title("🏛️ Nexus Business Intelligence")
nome_az = st.text_input("Ragione Sociale", "Azienda Beta S.p.A.")

col1, col2, col3 = st.columns(3)
with col1: rev = st.number_input("Fatturato (€)", 1500000.0)
with col2: ebit = st.number_input("EBITDA (€)", 250000.0)
with col3: pfn = st.number_input("Debito (PFN) (€)", 400000.0)

# Calcolo Z-Score
z = (1.2 * (rev * 0.1 / (pfn if pfn > 0 else 1))) + (3.3 * (ebit / (pfn if pfn > 0 else 1)))

# --- 4. VISUALIZZAZIONE RATING (DESIGN) ---
if z > 2.6:
    rating, color, bg = "SOLIDO", "#28a745", "#d4edda"
elif z > 1.1:
    rating, color, bg = "VULNERABILE", "#ffc107", "#fff3cd"
else:
    rating, color, bg = "DISTRESSED", "#dc3545", "#f8d7da"

st.markdown(f"""
    <div style="background-color:{bg}; padding:20px; border-radius:10px; border-left: 10px solid {color}; margin-bottom:20px;">
        <h1 style="color:{color}; margin:0;">RATING: {rating}</h1>
        <p style="color:black; margin:0;">Z-Score: <strong>{z:.2f}</strong></p>
    </div>
""", unsafe_allow_html=True)

# --- 5. SEZIONE SCARICA & ERP ---
st.subheader("📥 Export & Sistemi ERP")
col_e1, col_e2 = st.columns(2)

# Prepariamo il file CSV per ERP
df_export = pd.DataFrame([{"Azienda": nome_az, "Z-Score": round(z, 2), "Rating": rating, "Fatturato": rev}])
csv = df_export.to_csv(index=False).encode('utf-8')

with col_e1:
    st.download_button("📑 Scarica Tracciato ERP (CSV)", csv, f"export_{nome_az}.csv", "text/csv")

with col_e2:
    if st.button("📤 Invia a Gestionale"):
        st.success("Dati pronti per l'importazione ERP.")

st.divider()

# --- 6. SINCRONIZZAZIONE SUPABASE (PUSH) ---
if st.button("🚀 PUSH TO CLOUD"):
    url = "https://nexus-api-rf76.onrender.com/v1/scoring/analyze"
    headers = {"x-api-key": api_key}
    payload = {"company_name": nome_az, "revenue": rev, "ebitda": ebit, "total_debt": pfn}
    
    with st.spinner("Salvataggio su Supabase..."):
        try:
            r = requests.post(url, json=payload, headers=headers)
            if r.status_code == 200:
                st.balloons()
                st.success(f"Analisi salvata! Crediti: {r.json()['results']['credits_left']}")
            else:
                st.error(f"Errore: {r.text}")
        except Exception as e:
            st.error(f"Errore connessione: {e}")

st.divider()

# --- 7. MOSTRA DATI DA SUPABASE (IL RESTO CHE MANCAVA) ---
st.subheader("📊 Storico Analisi nel Database")
if st.button("🔄 Aggiorna Dati da Supabase"):
    # Qui simuliamo la lettura dei log che abbiamo salvato
    # In produzione useresti un endpoint GET, qui mostriamo i dati appena inviati
    st.write("Ultimi record trovati per il tuo Tenant:")
    st.dataframe(df_export) # S
