import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
from supabase import create_client, Client
import io

# --- 1. CONFIGURAZIONE E CONNESSIONE DB ---
st.set_page_config(page_title="Nexus Enterprise | AI Financial Hub", layout="wide", page_icon="🏛️")

@st.cache_resource
def init_supabase():
    """Connessione sicura a Supabase (non crasha se mancano le chiavi)"""
    try:
        if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
            return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except:
        return None
    return None

supabase = init_supabase()

if 'pdf_data' not in st.session_state:
    st.session_state.pdf_data = None

# --- 2. LOGICA DI ESTRAZIONE E CALCOLO ---

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
                val = pd.to_numeric(df[cols[alias]], errors='coerce').sum()
                if not pd.isna(val): data[key] = val
                break
    return data

def run_full_analysis(rev, ebitda, debt):
    """Motore Rating, Risk & Pricing"""
    rev = max(rev, 1)
    eb_val = max(ebitda, 1)
    db_val = max(debt, 1)
    
    # Altman Z-Score
    z = (1.2 * (rev*0.1/db_val)) + (3.3 * (eb_val/db_val))
    
    # Credit Risk & Pricing
    pd_rate = max(0.01, min(0.99, 1 / (z + 0.1) * 0.2))
    expected_loss = (rev * 0.10) * pd_rate * 0.45
    suggested_rate = (0.05 + pd_rate + 0.02) * 100
    
    status = "ECCELLENTE" if z > 2.6 else "STABILE" if z > 1.1 else "CRITICA"
    color = "#00CC66" if z > 2.6 else "#FFA500" if z > 1.1 else "#FF4B4B"
    
    return {
        "z": z, "status": status, "color": color, 
        "pd": pd_rate * 100, "el": expected_loss, "rate": suggested_rate,
        "ros": (eb_val/rev)*100, "lev": debt/eb_val
    }

def save_analysis(nome, res):
    """Salva i dati su Supabase se disponibile"""
    if supabase:
        try:
            data = {"company_name": nome, "z_score": res['z'], "status": res['status'], "expected_loss": res['el']}
            supabase.table("audit_reports").insert(data).execute()
        except: pass

# --- 3. INTERFACCIA SIDEBAR (INPUT & ERP) ---
with st.sidebar:
    st.title("🏛️ Nexus Control")
    st.subheader("📂 Importa ERP / Bilancio")
    uploaded_file = st.file_uploader("Trascina file Excel o CSV", type=["xlsx", "csv"])
    
    defaults = {"rev": 1000000, "ebit": 200000, "debt": 400000}
    if uploaded_file:
        try:
            df_file = pd.read_excel(uploaded_file) if "xlsx" in uploaded_file.name else pd.read_csv(uploaded_file)
            defaults = extract_financials(df_file)
            st.success("✅ Dati estratti con successo!")
        except Exception as e:
            st.error(f"Errore caricamento: {e}")

    st.divider()
    nome_az = st.text_input("Ragione Sociale", "Azienda Target S.p
