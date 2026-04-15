import streamlit as st
import plotly.graph_objects as go
from supabase import create_client
import pandas as pd

# --- IMPORT DAI NUOVI MODULI ---
from engine.scoring import calculate_metrics
from services.decision import get_credit_approval

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Coin-Nexus Enterprise", layout="wide")

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# --- LOGICA DI SALVATAGGIO (Versione Robust) ---
def push_to_db(company_name, metrics, decision):
    try:
        tenant_res = supabase.table("tenants").select("id").eq("name", "Doc Finance Partner").execute()
        if not tenant_res.data:
            tenant_res = supabase.table("tenants").insert({"name": "Doc Finance Partner", "api_key": "nexus_test_key_2024"}).execute()
        t_id = tenant_res.data[0]['id']

        comp_res = supabase.table("companies").upsert({"company_name": company_name, "tenant_id": t_id}, on_conflict="company_name").execute()
        c_id = comp_res.data[0]['id']

        supabase.table("credit_analyses").insert({
            "company_id": c_id,
            "financial_data": metrics,
            "dscr_value": metrics['dscr'],
            "leverage_value": metrics['leverage'],
            "rating_code": decision['rating'],
            "decision_output": decision['decision']
        }).execute()
        return True
    except Exception as e:
        st.error(f"Errore Database: {e}")
        return False

# --- INTERFACCIA UTENTE ---
st.title("🏛️ Coin-Nexus | Credit Decision Engine")
st.info("Motore di Audit Bancario Certificato")

tab1, tab2 = st.tabs(["📊 Analisi Real-time", "📜 Registro Audit"])

with tab1:
    col_in, col_out = st.columns([1, 2])
    with col_in:
        name = st.text_input("Ragione Sociale", "S.p.A. Target")
        rev = st.number_input("Ricavi", value=2000000)
        ebit = st.number_input("EBITDA", value=400000)
        deb = st.number_input("Debito Totale", value=600000)
        
        if st.button("ESEGUI AUDIT"):
            m = calculate_metrics({"revenue": rev, "ebitda": ebit, "debt": deb})
            d = get_credit_approval(m)
            
            if push_to_db(name, m, d):
                st.success("Analisi salvata nel database!")
                st.session_state['last_eval'] = (m, d, name)

    with col_out:
        if 'last_eval' in st.session_state:
            m, d, n = st.session_state['last_eval']
            st.subheader(f"Esito per {n}")
            
            c1, c2 = st.columns(2)
            c1.metric("Rating", d['rating'])
            c2.metric("Decisione", d['decision'])
            
            fig = go.Figure(go.Indicator(mode="gauge+number", value=m['dscr'], 
                            gauge={'axis':{'range':[0,5]}, 'bar':{'color': d['color']}}))
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    if st.button("Carica Storico"):
        res = supabase.table("credit_analyses").select("created_at, rating_code, decision_output, companies(company_name)").execute()
        if res.data:
            st.dataframe(pd.json_normalize(res.data), use_container_width=True)
