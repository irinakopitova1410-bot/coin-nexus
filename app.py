import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client, Client

# 1. Configurazione Professional
st.set_page_config(page_title="Coin-Nexus Enterprise", layout="wide", page_icon="🏛️")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 2. Connessione Sicura a Supabase
try:
    # Usa st.secrets per la produzione, o stringhe per test rapido
    SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://ipmttldwfsxuubugiyir.supabase.co")
    SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("❌ Errore Connessione Database")
    st.stop()

# 3. Import Moduli Locali
try:
    from engine.scoring import calculate_metrics
    from services.decision import get_credit_approval
    from utils.parser import extract_financials 
except ImportError:
    st.error("⚠️ Moduli engine non trovati.")
    st.stop()

# --- LOGICA STRATEGICA ---
def get_strategic_advice(m):
    advice = []
    if m.get('dscr', 0) < 1.2:
        gap_ebitda = (1.2 * m.get('debt', 0)) - m.get('ebitda', 0)
        advice.append({
            "icon": "⚠️", "label": "OTTIMIZZAZIONE DSCR", 
            "text": f"Soglia di sicurezza violata. Incrementare EBITDA di €{max(0, gap_ebitda):,.0f} per migliorare il rating."
        })
    if m.get('margin', 0) < 12.5:
        advice.append({
            "icon": "📊", "label": "PERFORMANCE", 
            "text": "Marginalità sotto benchmark (12.5%). Nexus suggerisce riduzione costi variabili del 3%."
        })
    if m.get('debt', 0) > (m.get('ebitda', 0) * 4):
        advice.append({
            "icon": "💸", "label": "LEVA FINANZIARIA", 
            "text": "Esposizione elevata. Consigliato consolidamento debito a medio/lungo termine."
        })
    return advice

def push_to_supabase(record):
    try:
        supabase.table("audit_reports").insert(record).execute()
        return True
    except Exception as e:
        st.error(f"Errore Cloud: {e}")
        return False

def get_enterprise_intelligence(metrics):
    cash_ratio = metrics.get('cash', 0) / max(1, metrics.get('short_debt', 0))
    materiality = metrics.get('revenue', 0) * 0.015
    rating_isp = "A1 - INVESTMENT GRADE" if metrics.get('dscr', 0) > 1.5 else "B2 - STABILE"
    return {"liquidity": round(cash_ratio, 2), "materiality": materiality, "rating_isp": rating_isp}

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏛️ CFO Dashboard")
    file = st.file_uploader("📂 ERP Flow (CSV/XLSX)", type=["xlsx", "csv"])
    data = {"revenue": 1000000, "ebitda": 200000, "debt": 400000, "cash": 80000, "short_debt": 100000, "data_quality": "n/a", "data_issues": []}
    
    if file:
        df = pd.read_excel(file) if "xlsx" in file.name else pd.read_csv(file)
        data.update(extract_financials(df))
    
    st.divider()
    nome_azienda = st.text_input("Ragione Sociale", "Azienda Target S.p.A.")
    rev_in = st.number_input("Fatturato (€)", value=int(data['revenue']))
    ebit_in = st.number_input("EBITDA (€)", value=int(data['ebitda']))
    pfn_in = st.number_input("PFN (€)", value=int(data['debt']))

# --- MAIN UI ---
st.title("📊 Financial Dossier: Analisi di Merito Creditizio")
st.caption("Nexus Enterprise Engine | Conforme Basilea III")

if st.button("🚀 GENERA REPORT CERTIFICATO", use_container_width=True):
    m = calculate_metrics({"revenue": rev_in, "ebitda": ebit_in, "debt": pfn_in, "short_debt": data['short_debt'], "cash": data['cash']})
    intel = get_enterprise_intelligence(m)
    res = get_credit_approval(m)

    # 1. KPI Principali
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rating Intesa SP", intel['rating_isp'])
    c2.metric("Score Audit", f"{res.get('score', 0)}/100")
    c3.metric("Materialità ISA 320", f"€ {intel['materiality']:,.0f}")
    c4.metric("Acid Test", intel['liquidity'])

    # 2. Strategic Advice (L'effetto WOW)
    st.divider()
    st.subheader
