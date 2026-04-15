import streamlit as st
import plotly.graph_objects as go
from supabase import create_client
import pandas as pd
from engine.scoring import calculate_metrics
from services.decision import get_credit_approval

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Coin-Nexus Enterprise", layout="wide")

# Connessione a Supabase
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# --- FUNZIONE SALVATAGGIO ---
def push_to_db(name, m, d):
    try:
        # Recupero Tenant
        res = supabase.table("tenants").select("id").eq("name", "Doc Finance Partner").execute()
        t_id = res.data[0]['id']
        # Upsert Azienda
        comp = supabase.table("companies").upsert({"company_name": name, "tenant_id": t_id}, on_conflict="company_name").execute()
        c_id = comp.data[0]['id']
        # Insert Analisi
        supabase.table("credit_analyses").insert({
            "company_id": c_id, "dscr_value": m['dscr'], "leverage_value": m['leverage'],
            "rating_code": d['rating'], "decision_output": d['decision']
        }).execute()
        return True
    except: return False

# --- UI ---
st.title("🏛️ Coin-Nexus | Credit Decision Engine")

tab1, tab2 = st.tabs(["📊 Analisi e Report", "📜 Registro Storico"])

with tab1:
    c1, c2 = st.columns([1, 2])
    with c1:
        name = st.text_input("Ragione Sociale", "Azienda Target S.p.A.")
        rev = st.number_input("Ricavi (€)", value=1500000)
        ebit = st.number_input("EBITDA (€)", value=300000)
        debt = st.number_input("Debito (€)", value=400000)
        
        if st.button("ESEGUI AUDIT E GENERA REPORT"):
            m = calculate_metrics({"revenue": rev, "ebitda": ebit, "debt": debt})
            d = get_credit_approval(m)
            st.session_state['res'] = (m, d, name)
            push_to_db(name, m, d)

    with c2:
        if 'res' in st.session_state:
            m, d, n = st.session_state['res']
            st.subheader(f"Risultato: {d['rating']}")
            st.write(f"Esito: **{d['decision']}**")
            
            # Gauge Chart
            fig = go.Figure(go.Indicator(mode="gauge+number", value=m['dscr'], 
                            title={'text': "DSCR Index"},
                            gauge={'axis': {'range': [0, 5]}, 'bar': {'color': d['color']}}))
            st.plotly_chart(fig, use_container_width=True)
            
            # TASTO REPORT (Simulato come TXT per velocità, scaricabile)
            report_data = f"REPORT AUDIT COIN-NEXUS\nEmpresa: {n}\nRating: {d['rating']}\nDSCR: {m['dscr']}\nDecision: {d['decision']}"
            st.download_button("📥 SCARICA REPORT AUDIT", report_data, file_name=f"Report_{n}.txt")

with tab2:
    if st.button("Aggiorna Storico dal Database"):
        res = supabase.table("credit_analyses").select("created_at, rating_code, decision_output, companies(company_name)").execute()
        if res.data:
            st.dataframe(pd.json_normalize(res.data))
