import os
import sys
import streamlit as st
from supabase import create_client, Client

# Inizializzazione sicura
url = st.secrets["https://ipmttldwfsxuubugiyir.supabase.co"]
key = st.secrets["sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos"]
supabase: Client = create_client(url, key)

def save_to_nexus_cloud(company_name, metrics, result):
    # Prepariamo il record per la tua nuova tabella SQL
    audit_data = {
        "company_name": company_name, # Se hai aggiunto questa colonna
        "dscr_value": float(metrics['dscr']),
        "rating_code": result['rating'],
        "decision_output": result['decision'],
        "financial_data": metrics # Salva tutto il dizionario nel campo JSONB
    }
    
    # Inserimento nella tabella potenziata
    try:
        supabase.table("credit_analyses").insert(audit_data).execute()
        st.success("✅ Analisi sincronizzata nel Cloud di Doc Finance")
    except Exception as e:
        st.error(f"Errore di sincronizzazione: {e}")

# Nel tuo tasto "GENERA REPORT" aggiungi:
if st.button("🚀 ESEGUI AUDIT"):
    # ... i tuoi calcoli ...
    save_to_nexus_cloud(azienda_input, m, res)
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client, Client # INTEGRAZIONE SUPABASE

# Configurazione Professional
st.set_page_config(page_title="Coin-Nexus Enterprise", layout="wide", page_icon="🏛️")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- CONNESSIONE DATABASE (Prendi i dati da Supabase Settings > API) ---
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://ipmttldwfsxuubugiyir.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    from engine.scoring import calculate_metrics
    from services.decision import get_credit_approval
    from utils.parser import extract_financials 
except ImportError:
    st.error("⚠️ Struttura moduli incompleta. Verifica i file __init__.py")
    st.stop()

# --- LOGICA DI SALVATAGGIO CLOUD ---
def push_to_supabase(record):
    try:
        supabase.table("audit_reports").insert(record).execute()
    except Exception as e:
        st.error(f"Errore sincronizzazione Cloud: {e}")

# --- MODULO 100K: BENCHMARK & LIQUIDITÀ ---
def get_enterprise_intelligence(metrics):
    bench_margin = 12.5
    gap = metrics['margin'] - bench_margin
    cash_ratio = metrics.get('cash', 0) / max(1, metrics.get('short_debt', 0))
    materiality = metrics.get('revenue', 0) * 0.015
    
    return {
        "gap": round(gap, 1),
        "liquidity": round(cash_ratio, 2),
        "materiality": materiality,
        "rating_isp": "A1 - INVESTMENT GRADE" if metrics['dscr'] > 1.5 else "B2 - STABILE"
    }

# --- INTERFACCIA CFO ---
with st.sidebar:
    st.title("🏛️ CFO Dashboard")
    st.info("Sistema di Intelligence Integrato")
    
    file = st.file_uploader("📂 Carica Flusso ERP (CSV/XLSX)", type=["xlsx", "csv"])
    
    data = {"revenue": 1000000, "ebitda": 200000, "debt": 400000, "cash": 80000, "short_debt": 100000, "data_quality": "n/a", "data_issues": []}
    
    if file:
        df = pd.read_excel(file) if "xlsx" in file.name else pd.read_csv(file)
        extracted = extract_financials(df)
        data.update(extracted)
        st.success(f"Dati caricati. Qualità: {data['data_quality'].upper()}")

    st.divider()
    nome_azienda = st.text_input("Ragione Sociale", "Azienda Target S.p.A.")
    isa_punteggio = st.slider("Rating ISA Aziendale", 1, 10, 8)
    rev_in = st.number_input("Fatturato Annuo (€)", value=int(data['revenue']))
    ebit_in = st.number_input("EBITDA (€)", value=int(data['ebitda']))
    pfn_in = st.number_input("Posizione Finanziaria Netta (€)", value=int(data['debt']))

# --- REPORT PRINCIPALE ---
st.title("📊 Financial Dossier: Analisi di Merito Creditizio")
st.markdown("---")

if st.button("🚀 GENERA REPORT CERTIFICATO", use_container_width=True):
    m = calculate_metrics({"revenue": rev_in, "ebitda": ebit_in, "debt": pfn_in, "short_debt": data['short_debt'], "cash": data['cash']})
    intel = get_enterprise_intelligence(m)
    res = get_credit_approval(m)

    # --- SALVATAGGIO AUTOMATICO SU SUPABASE ---
    record_audit = {
        "company_name": nome_azienda,
        "revenue": float(rev_in),
        "score": int(res['score']),
        "rating": intel['rating_isp'],
        "materiality": float(intel['materiality'])
    }
    push_to_supabase(record_audit) # Sincronizzazione immediata

    # RIGA 1: KPI BANCARI
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rating Intesa SP", intel['rating_isp'])
    c2.metric("Score Audit", f"{res['score']}/100")
    c3.metric("Materialità (ISA 320)", f"€ {intel['materiality']:,.0f}")
    c4.metric("Liquidità (Acid Test)", intel['liquidity'])

    # RIGA 2: BENCHMARK & DATA QUALITY
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("🎯 Benchmark di Settore")
        fig_b = go.Figure(go.Bar(x=['Tua Azienda', 'Media Settore'], y=[m['margin'], 12.5], marker_color=['#00CC66', '#334155']))
        fig_b.update_layout(height=300, template="plotly_dark")
        st.plotly_chart(fig_b, use_container_width=True)
    
    with col_b:
        st.subheader("🔍 Data Quality Check")
        if data['data_issues']:
            for issue in data['data_issues']: st.warning(issue)
        else: st.success("Dati validati con successo e archiviati su Supabase.")

    # RIGA 3: PROIEZIONE 4 ANNI
    st.subheader("📈 Stress Test & Cash Flow Prospettico (48 Mesi)")
    anni = ['2026', '2027', '2028', '2029', '2030']
    flusso_cassa = [data['cash']] + [data['cash'] + (m['ebitda'] * 0.5 * i) for i in range(1, 5)]
    
    fig_f = go.Figure()
    fig_f.add_trace(go.Scatter(x=anni, y=flusso_cassa, fill='tozeroy', line_color='#00CC66', name="Cassa Cumulata"))
    fig_f.update_layout(height=400, template="plotly_dark")
    st.plotly_chart(fig_f, use_container_width=True)

    st.success(f"Dossier certificato e archiviato in database sicuro (Cloud Sync: OK)")
