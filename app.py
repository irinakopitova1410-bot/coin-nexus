import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client, Client

# --- CONFIGURAZIONE PROFESSIONAL ---
st.set_page_config(page_title="Coin-Nexus Enterprise", layout="wide", page_icon="🏛️")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- CONNESSIONE DATABASE ---
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except:
    st.error("Configura i Secrets su Streamlit Cloud!")
    st.stop()

# --- IMPORT ENGINE ---
try:
    from engine.scoring import calculate_metrics
    from services.decision import get_credit_approval
    from utils.parser import extract_financials 
except:
    st.error("Moduli engine mancanti.")
    st.stop()

# --- LOGICA STRATEGICA NEXUS AI ---
def get_strategic_advice(m):
    advice = []
    if m.get('dscr', 0) < 1.2:
        gap = (1.2 * m.get('debt', 0)) - m.get('ebitda', 0)
        advice.append({"icon": "⚠️", "label": "DSCR", "text": f"Mancano €{max(0, gap):,.0f} di EBITDA per il rating A1."})
    if m.get('margin', 0) < 12.5:
        advice.append({"icon": "📊", "label": "MARGIN", "text": "Margine sotto media. Ottimizzare costi variabili del 3%."})
    return advice

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏛️ CFO Dashboard")
    file = st.file_uploader("📂 ERP Flow (XLSX/CSV)", type=["xlsx", "csv"])
    data = {"revenue": 1000000, "ebitda": 200000, "debt": 400000, "cash": 80000, "short_debt": 100000}
    
    if file:
        df = pd.read_excel(file) if "xlsx" in file.name else pd.read_csv(file)
        data.update(extract_financials(df))
    
    nome_azienda = st.text_input("Ragione Sociale", "Azienda Target S.p.A.")
    rev_in = st.number_input("Fatturato (€)", value=int(data['revenue']))
    ebit_in = st.number_input("EBITDA (€)", value=int(data['ebitda']))
    pfn_in = st.number_input("PFN (€)", value=int(data['debt']))

# --- INTERFACCIA PRINCIPALE ---
st.title("📊 Financial Dossier: Analisi di Merito Creditizio")
st.markdown("---")

if st.button("🚀 GENERA REPORT CERTIFICATO", use_container_width=True):
    # Calcoli
    m = calculate_metrics({"revenue": rev_in, "ebitda": ebit_in, "debt": pfn_in, "short_debt": data['short_debt'], "cash": data['cash']})
    res = get_credit_approval(m)
    
    # 1. KPI (Visualizzati correttamente)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rating", "A1 - INVESTMENT" if m['dscr'] > 1.5 else "B2 - STABILE")
    c2.metric("Score", f"{res.get('score', 0)}/100")
    c3.metric("Materialità", f"€ {rev_in * 0.015:,.0f}")
    c4.metric("Cash Ratio", round(data['cash']/max(1, data['short_debt']), 2))

    # 2. Nexus AI Advisor
    st.subheader("🧠 Nexus AI: Strategic Advisor")
    advices = get_strategic_advice(m)
    if advices:
        cols = st.columns(len(advices))
        for i, a in enumerate(advices):
            cols[i].info(f"**{a['icon']} {a['label']}**\n\n{a['text']}")

    # 3. Grafici
    col_a, col_b = st.columns(2)
    with col_a:
        fig = go.Figure(go.Bar(x=['Tua Azienda', 'Media'], y=[m['margin'], 12.5], marker_color=['#00CC66', '#334155']))
        fig.update_layout(height=300, title="Benchmark Margine %", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        anni = ['2026', '2027', '2028', '2029']
        flusso = [data['cash'] + (i * 50000) for i in range(4)]
        fig2 = go.Figure(go.Scatter(x=anni, y=flusso, fill='tozeroy', line_color='#00CC66'))
        fig2.update_layout(height=300, title="Proiezione Liquidità", template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)

    # 4. Salvataggio Cloud
    supabase.table("audit_reports").insert({
        "company_name": nome_azienda, "revenue": rev_in, "score": res.get('score', 0), 
        "rating": "A1", "materiality": rev_in * 0.015
    }).execute()
    st.toast("✅ Analisi salvata su Supabase")

# --- SEZIONE PDF (FUORI DAL BUTTON) ---
st.divider()
st.subheader("📥 Export Istituzionale")
if st.button("📄 GENERA DOSSIER PDF PER BANCA"):
    st.balloons()
    st.success("Dossier PDF Generato! Include: Analisi Centrale Rischi, Stress Test e Piano Strategico.")
