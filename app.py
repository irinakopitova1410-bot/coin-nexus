import streamlit as st
import plotly.graph_objects as go
from supabase import create_client
import pandas as pd

# Import dai moduli strutturati
try:
    from engine.scoring import calculate_metrics
    from services.decision import get_credit_approval
except ImportError:
    st.error("Errore: Assicurati che le cartelle 'engine' e 'services' abbiano i file __init__.py")

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Coin-Nexus Enterprise", layout="wide")

# Connessione sicura
@st.cache_resource
def init_connection():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except Exception as e:
        st.error(f"Errore connessione Supabase: Controlla i Secrets su Streamlit Cloud.")
        return None

supabase = init_connection()

# --- LOGICA DI SALVATAGGIO ---
def push_to_db(company_name, metrics, decision):
    if not supabase: return False
    try:
        # 1. Recupero Tenant
        res = supabase.table("tenants").select("id").eq("name", "Doc Finance Partner").execute()
        if not res.data:
            # Se non esiste lo creiamo al volo
            res = supabase.table("tenants").insert({"name": "Doc Finance Partner", "api_key": "test_key"}).execute()
        t_id = res.data[0]['id']

        # 2. Upsert Azienda
        comp = supabase.table("companies").upsert({"company_name": company_name, "tenant_id": t_id}, on_conflict="company_name").execute()
        c_id = comp.data[0]['id']

        # 3. Inserimento Analisi
        supabase.table("credit_analyses").insert({
            "company_id": c_id,
            "dscr_value": metrics['dscr'],
            "leverage_value": metrics['leverage'],
            "rating_code": decision['rating'],
            "decision_output": decision['decision']
        }).execute()
        return True
    except Exception as e:
        st.warning(f"Database in sola lettura o errore RLS: {e}")
        return False

# --- INTERFACCIA ---
st.title("🏛️ Coin-Nexus | Credit Engine")

tab1, tab2 = st.tabs(["📊 Terminale", "📜 Storico"])

with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        name = st.text_input("Azienda", "Srl di Esempio")
        rev = st.number_input("Ricavi", value=1000000)
        ebit = st.number_input("EBITDA", value=200000)
        debt = st.number_input("Debito", value=300000)
        
        if st.button("ESEGUI ANALISI"):
            m = calculate_metrics
