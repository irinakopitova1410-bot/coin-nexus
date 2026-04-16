import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
from supabase import create_client, Client
import io

# --- 1. CONFIGURAZIONE E CONNESSIONE ---
st.set_page_config(page_title="Nexus Enterprise | AI Financial Hub", layout="wide", page_icon="🏛️")

@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["https://ipmttldwfsxuubugiyir.supabase.co"]
        key = st.secrets["sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos"]
        return create_client(url, key)
    except:
        return None

supabase = init_supabase()

if 'pdf_data' not in st.session_state:
    st.session_state.pdf_data = None

# --- 2. MOTORI DI CALCOLO E ESTRAZIONE ---

def extract_financials(df):
    """Mappa automaticamente le colonne del bilancio ERP/Excel"""
    cols = {c.lower(): c for c in df.columns}
    data = {"rev": 1000000, "ebit": 200000, "debt": 400000}
    mapping = {
        "rev": ['fatturato', 'revenue', 'vendite', 'valore della produzione'],
        "ebit": ['ebitda', 'mol', 'margine operativo lordo'],
        "debt": ['debito', 'debt', 'pfn', 'debiti finanziari']
    }
    for key, aliases in mapping.items():
        for alias in aliases:
            if alias in cols:
                data[key] = pd.to_numeric(df[cols[alias]], errors='coerce').sum()
                break
    return data

def run_full_analysis(rev, ebitda, debt):
    rev = max(rev, 1)
    ebitda_val = max(ebitda, 1)
    
    # Altman Z-Score
    z = (1.2 * (rev*0.1/max(debt,1))) + (3.3 * (ebitda_val/max(debt,1)))
    
    # Credit Risk Metrics
    pd_rate = max(0.01, min(0.99, 1 / (z + 0.1) * 0.2))
    expected_loss = (rev * 0.10) * pd_rate * 0.45
    suggested_rate = (0.05 + pd_rate + 0.02) * 100
    
    status = "ECCELLENTE" if z > 2.6 else "STABILE" if z > 1.1 else "CRITICA"
    color = "#00CC66" if z > 2.6 else "#FFA500" if z > 1.1 else "#FF4B4B"
    
    return {
        "z": z, "status": status, "color": color, 
        "pd": pd_rate * 100, "el": expected_loss, "rate": suggested_rate,
        "ros": (ebitda_val/rev)*100, "lev": debt/ebitda_val
    }

def save_analysis(nome, res):
    if supabase:
        try:
            data = {
                "company_name": nome, "z_score": res['z'], 
                "status": res['status'], "expected_loss": res['el']
            }
            supabase.table("audit_reports").insert(data).execute()
            return True
        except: return False
    return False

# --- 3. SIDEBAR: CARICAMENTO ERP ---
with st.sidebar:
    st.title("🏛️ Nexus Control")
    st.subheader("📂 Importa ERP/Bilancio")
    uploaded_file = st.file_uploader("Carica Excel o CSV", type=["xlsx", "csv"])
    
    defaults = {"rev": 1000000, "ebit": 200000, "debt": 400000}
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file) if "xlsx" in uploaded_file.name else pd.read_csv(uploaded_file)
            defaults = extract_financials(df)
            st.success("✅ Dati estratti!")
        except Exception as e: st.error(f"Errore: {e}")

    st.divider()
    nome = st.text_input("Ragione Sociale", "Azienda Target S.p.A.")
    rev_in = st.number_input("Fatturato (€)", value=int(defaults['rev']))
    ebit_in = st.number_input("EBITDA (€)", value=int(defaults['ebit']))
    pfn_in = st.number_input("Debito Finanziario (€)", value=int(defaults['debt']))
    
    st.divider()
    opt_deep = st.toggle("🔍 Deep Audit (Indici)", value=
