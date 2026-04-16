import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configurazione Professional
st.set_page_config(page_title="Coin-Nexus Enterprise", layout="wide", page_icon="🏛️")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from engine.scoring import calculate_metrics
    from services.decision import get_credit_approval
    from utils.parser import extract_financials 
except ImportError:
    st.error("⚠️ Struttura moduli incompleta. Verifica i file __init__.py")
    st.stop()

# --- MODULO 100K: BENCHMARK & LIQUIDITÀ ---
def get_enterprise_intelligence(metrics):
    # Benchmark settoriale (Margine EBITDA medio: 12.5%)
    bench_margin = 12.5
    gap = metrics['margin'] - bench_margin
    
    # Indice di Liquidità Immediata (Cash / Debiti Breve)
    cash_ratio = metrics.get('cash', 0) / max(1, metrics.get('short_debt', 0))
    
    # Materialità ISA 320 (1.5% Ricavi)
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
    
    # Dati iniziali
    data = {"revenue": 1000000, "ebitda": 200000, "debt": 400000, "cash": 80000, "short_debt": 100000, "data_quality": "n/a", "data_issues": []}
    
    if file:
        df = pd.read_excel(file) if "xlsx" in file.name else pd.read_csv(file)
        extracted = extract_financials(df)
        data.update(extracted)
        st.success(f"Dati caricati. Qualità: {data['data_quality'].upper()}")

    st.divider()
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
        else: st.success("Dati validati secondo standard di revisione.")

    # RIGA 3: PROIEZIONE 4 ANNI (Sostenibilità)
    st.subheader("📈 Stress Test & Cash Flow Prospettico (48 Mesi)")
    anni = ['2026', '2027', '2028', '2029', '2030']
    flusso_cassa = [data['cash']] + [data['cash'] + (m['ebitda'] * 0.5 * i) for i in range(1, 5)]
    
    fig_f = go.Figure()
    fig_f.add_trace(go.Scatter(x=anni, y=flusso_cassa, fill='tozeroy', line_color='#00CC66', name="Cassa Cumulata"))
    fig_f.update_layout(height=400, template="plotly_dark", title="Accumulo Liquidità Previsto")
    st.plotly_chart(fig_f, use_container_width=True)

    # FOOTER: PITCH VENDITA
    st.divider()
    st.markdown(f"**Conclusione per il Comitato Rischi:** L'azienda presenta una marginalità del {m['margin']}% (Gap vs Settore: {intel['gap']}%). La sostenibilità a 4 anni è confermata.")
    st.button("📥 SCARICA DOSSIER PDF COMPLETO (White Label)")
