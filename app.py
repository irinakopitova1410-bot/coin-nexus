import streamlit as st
import requests

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Nexus Engine | Business Intelligence", layout="wide")

# --- 2. INIZIALIZZAZIONE VARIABILI (Evita NameError) ---
# Definiamo i valori di default in modo che le variabili esistano sempre
nome_az = "Azienda Demo S.r.l."
rev_in = 1000000.0
ebit_in = 150000.0
pfn_in = 500000.0

# --- 3. SIDEBAR - INPUT DATI ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135706.png", width=80)
    st.header("📝 Input Dati Finanziari")
    
    nome_az = st.text_input("Ragione Sociale", value=nome_az)
    rev_in = st.number_input("Fatturato (€)", value=rev_in, step=10000.0)
    ebit_in = st.number_input("EBITDA (€)", value=ebit_in, step=5000.0)
    pfn_in = st.number_input("Debito Totale (PFN) (€)", value=pfn_in, step=10000.0)
    
    st.divider()
    st.caption("Nexus Engine v1.0.1 - Powered by Doc-Finance")

# --- 4. LOGICA DI CALCOLO LOCALE (Basilea IV) ---
# Calcolo rapido dello Z-Score locale
debt_safe = pfn_in if pfn_in > 0 else 1
z_score_local = (1.2 * (rev_in * 0.1 / debt_safe)) + (3.3 * (ebit_in / debt_safe))

if z_score_local > 2.6:
    rating_local = "SOLIDO"
    color = "green"
elif z_score_local > 1.1:
    rating_local = "VULNERABILE"
    color = "orange"
else:
    rating_local = "DISTRESSED"
    color = "red"

# --- 5. DASHBOARD PRINCIPALE ---
st.title("🏛️ Nexus Engine Dashboard")
st.write(f"Analisi finanziaria per: **{nome_az}**")

col1, col2, col3 = st.columns(3)
col1.metric("Fatturato", f"€ {rev_in:,.0f}")
col2.metric("EBITDA", f"€ {ebit_in:,.0f}")
col3.metric("Z-Score", f"{z_score_local:.2f}", delta=rating_local, delta_color="normal")

st.divider()

# --- 6. ADMIN PANEL & ENTERPRISE SYNC ---
st.subheader("📜 Admin Panel - Data Logs & API")

# Creiamo il pacchetto dati (Payload) completo come richiesto
payload_demo = {
    "company_name": nome_az,
    "revenue": rev_in,
    "ebitda": ebit_in,
    "total_debt": pfn_in,
    "z_score_local": round(z_score_local, 2),
    "rating_local": rating_local
}

col_json, col_api = st.columns([1, 1])

with col_json:
    st.info("📦 JSON Payload pronto per l'export:")
    st.json(payload_demo)

with col_api:
    st.warning("🔗 Enterprise Integration (Render + Supabase)")
    st.write("Invia questa analisi al database centralizzato di Doc-Finance.")
    
    if st.button("🚀 PUSH TO DOC-FINANCE"):
        # URL del tuo backend su Render
        url_render = "https://nexus-api-rf76.onrender.com/v1/scoring/analyze"
        # API Key che abbiamo verificato su Supabase
        headers = {"x-api-key": "nexus_test_key_2026"}
        
        with st.spinner("Connessione al server Render in corso..."):
            try:
                # Chiamata API al backend
                response = requests.
