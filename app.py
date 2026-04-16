import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client, Client

# 1. Configurazione Professional
st.set_page_config(page_title="Coin-Nexus Enterprise", layout="wide", page_icon="🏛️")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 2. Connessione Sicura a Supabase (Utilizza i Secrets configurati sopra)
try:
SUPABASE_URL = "https://ipmttldwfsxuubugiyir.supabase.co"
SUPABASE_KEY = "sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos"
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("❌ Errore Secrets: Configura SUPABASE_URL e SUPABASE_KEY nelle impostazioni di Streamlit.")
    st.stop()

# 3. Import Moduli Locali
try:
    from engine.scoring import calculate_metrics
    from services.decision import get_credit_approval
    from utils.parser import extract_financials 
except ImportError:
    st.error("⚠️ Struttura moduli incompleta. Verifica i file __init__.py nelle cartelle.")
    st.stop()

# --- LOGICA DI SALVATAGGIO CLOUD ---
def push_to_supabase(record):
    """Invia i dati alla tabella audit_reports"""
    try:
        supabase.table("audit_reports").insert(record).execute()
        return True
    except Exception as e:
        st.error(f"Errore sincronizzazione Cloud: {e}")
        return False

# --- MODULO INTELLIGENCE: BENCHMARK & LIQUIDITÀ ---
def get_enterprise_intelligence(metrics):
    bench_margin = 12.5
    gap = metrics['margin'] - bench_margin
    # Calcolo Liquidità (Acid Test)
    cash_ratio = metrics.get('cash', 0) / max(1, metrics.get('short_debt', 0))
    # Materialità ISA 320 (1.5% Ricavi)
    materiality = metrics.get('revenue', 0) * 0.015
    
    rating_isp = "A1 - INVESTMENT GRADE" if metrics.get('dscr', 0) > 1.5 else "B2 - STABILE"
    
    return {
        "gap": round(gap, 1),
        "liquidity": round(cash_ratio, 2),
        "materiality": materiality,
        "rating_isp": rating_isp
    }

# --- SIDEBAR: INPUT & ERP ---
with st.sidebar:
    st.title("🏛️ CFO Dashboard")
    st.info("Sistema di Intelligence Integrato")
    
    file = st.file_uploader("📂 Carica Flusso ERP (CSV/XLSX)", type=["xlsx", "csv"])
    
    # Valori iniziali di backup
    data = {"revenue": 1000000, "ebitda": 200000, "debt": 400000, "cash": 80000, "short_debt": 100000, "data_quality": "n/a", "data_issues": []}
    
    if file:
        try:
            df = pd.read_excel(file) if "xlsx" in file.name else pd.read_csv(file)
            extracted = extract_financials(df)
            data.update(extracted)
            st.success(f"Dati caricati. Qualità: {data['data_quality'].upper()}")
        except Exception as e:
            st.error(f"Errore lettura file: {e}")

    st.divider()
    nome_azienda = st.text_input("Ragione Sociale", "Azienda Target S.p.A.")
    rev_in = st.number_input("Fatturato Annuo (€)", value=int(data['revenue']))
    ebit_in = st.number_input("EBITDA (€)", value=int(data['ebitda']))
    pfn_in = st.number_input("Posizione Finanziaria Netta (€)", value=int(data['debt']))

# --- REPORT PRINCIPALE ---
st.title("📊 Financial Dossier: Analisi di Merito Creditizio")
st.caption("Standard di analisi conforme ai modelli di rating Basilea III / Intesa Sanpaolo")
st.markdown("---")

if st.button("🚀 GENERA REPORT CERTIFICATO", use_container_width=True):
    # Esecuzione Motore di Analisi
    m = calculate_metrics({
        "revenue": rev_in, 
        "ebitda": ebit_in, 
        "debt": pfn_in, 
        "short_debt": data['short_debt'], 
        "cash": data['cash']
    })
    intel = get_enterprise_intelligence(m)
    res = get_credit_approval(m)

    # --- SINCRONIZZAZIONE DATABASE SUPABASE ---
    record_audit = {
        "company_name": nome_azienda,
        "revenue": float(rev_in),
        "score": int(res.get('score', 0)),
        "rating": intel['rating_isp'],
        "materiality": float(intel['materiality'])
    }
    
    with st.spinner("Archiviazione nel Cloud Nexus..."):
        success = push_to_supabase(record_audit)

    # VISUALIZZAZIONE KPI
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rating Intesa SP", intel['rating_isp'])
    c2.metric("Score Audit", f"{res.get('score', 0)}/100")
    c3.metric("Materialità (ISA 320)", f"€ {intel['materiality']:,.0f}")
    c4.metric("Liquidità (Acid Test)", intel['liquidity'])

    # GRAFICI
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("🎯 Benchmark di Settore")
        fig_b = go.Figure(go.Bar(
            x=['Tua Azienda', 'Media Settore'], 
            y=[m.get('margin', 0), 12.5], 
            marker_color=['#00CC66', '#334155']
        ))
        fig_b.update_layout(height=300, template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_b, use_container_width=True)
    
    with col_b:
        st.subheader("📈 Proiezione Cash Flow (48 Mesi)")
        anni = ['2026', '2027', '2028', '2029', '2030']
        flusso_cassa = [data['cash']] + [data['cash'] + (m.get('ebitda', 0) * 0.5 * i) for i in range(1, 5)]
        fig_f = go.Figure(go.Scatter(x=anni, y=flusso_cassa, fill='tozeroy', line_color='#00CC66'))
        fig_f.update_layout(height=300, template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_f, use_container_width=True)

    if success:
        st.success(f"✔️ Dossier per {nome_azienda} certificato e archiviato in database sicuro.")
    
    st.divider()
    st.button("📥 SCARICA DOSSIER PDF COMPLETO (White Label)")
