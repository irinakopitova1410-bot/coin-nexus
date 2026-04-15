import streamlit as st
from supabase import create_client, Client
from scoring import NexusScorer
import plotly.graph_objects as go

# Collegamento sicuro ai Secrets (da impostare sulla dashboard di Streamlit)
url = st.secrets["https://ipmttldwfsxuubugiyir.supabase.co"]
key = st.secrets["sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Coin-Nexus SaaS", layout="wide", page_icon="🏛️")

st.title("🏛️ Coin-Nexus | Cloud Terminal")

# Sidebar per Input
with st.sidebar:
    st.header("👤 Utente Enterprise")
    company = st.text_input("Ragione Sociale", "Azienda Beta S.r.l.")
    rev = st.number_input("Ricavi (€)", value=2500000)
    costs = st.number_input("Costi (€)", value=1800000)
    debt = st.number_input("Debito (€)", value=400000)
    run = st.button("🚀 ESEGUI & SALVA")

if run:
    scorer = NexusScorer(rev, costs, debt)
    rating, desc = scorer.get_nexus_rating()
    
    # SALVATAGGIO NEL DATABASE
    try:
        data = {
            "company_name": company,
            "rating": rating,
            "revenue": rev,
            "ebitda": rev - costs
        }
        supabase.table("audit_reports").insert(data).execute()
        st.success(f"Analisi per {company} salvata nel Cloud!")
    except Exception as e:
        st.error(f"Errore database: {e}")

    # Visualizzazione Risultati
    st.metric("Rating Basilea IV", rating, desc)
    # Qui aggiungi i tuoi grafici professionali...

# VISUALIZZAZIONE STORICO (Il vero valore del SaaS)
st.divider()
st.subheader("📑 Database Storico Aziende Analizzate")
try:
    response = supabase.table("audit_reports").select("*").order("created_at", desc=True).execute()
    if response.data:
        st.dataframe(response.data, use_container_width=True)
except Exception as e:
    st.info("Inizia la prima analisi per popolare il database.")
