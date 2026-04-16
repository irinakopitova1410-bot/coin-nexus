import streamlit as st
import pandas as pd
# Import dai moduli (assicurati che esistano i file __init__.py nelle cartelle)
try:
    from engine.scoring import calculate_metrics
    from services.decision import get_credit_approval
except ImportError as e:
    st.error(f"Errore di importazione moduli: {e}. Controlla i file __init__.py")

# --- TITOLO E UI ---
st.title("🏛️ Coin-Nexus | Credit Decision Engine")

# Verifica se i Secrets sono configurati
if "SUPABASE_URL" not in st.secrets:
    st.warning("⚠️ Configura i Secrets (SUPABASE_URL e KEY) su Streamlit Cloud per attivare il database.")
else:
    st.success("✅ Connessione Cloud Pronta")

# --- LOGICA DI INPUT ---
with st.sidebar:
    st.header("Dati Aziendali")
    name = st.text_input("Ragione Sociale", "Esempio S.p.A.")
    rev = st.number_input("Ricavi (€)", value=1000000)
    ebitda = st.number_input("EBITDA (€)", value=200000)
    debt = st.number_input("Debito Totale (€)", value=400000)

if st.button("ESEGUI AUDIT BANCARIO"):
    # Esegue i calcoli usando i tuoi moduli engine e services
    metrics = calculate_metrics({"revenue": rev, "ebitda": ebitda, "debt": debt})
    decision = get_credit_approval(metrics)
    
    # Mostra i risultati
    col1, col2 = st.columns(2)
    col1.metric("Rating", decision['rating'])
    col2.metric("Esito", decision['decision'])
    
    st.write("### Dettaglio Metriche")
    st.json(metrics)
    
    # Tasto Report
    st.download_button("📥 Scarica Report Audit", f"Audit per {name}: {decision['decision']}", file_name="audit.txt")
