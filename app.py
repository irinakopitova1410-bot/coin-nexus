import streamlit as st
import plotly.graph_objects as go
from supabase import create_client
import pandas as pd
# Importiamo il motore dal modulo che hai creato
from engine.scoring import calculate_metrics, get_credit_decision

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Coin-Nexus Enterprise", layout="wide")

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# --- LOGICA DI SALVATAGGIO ---
def push_to_db(company_name, metrics, decision):
    try:
        # Cerchiamo il partner 'Doc Finance Partner'
        tenant_res = supabase.table("tenants").select("id").eq("name", "Doc Finance Partner").execute()
        
        # Se non esiste, lo creiamo (fondamentale per evitare l'errore PGRST116)
        if not tenant_res.data:
            tenant_res = supabase.table("tenants").insert({
                "name": "Doc Finance Partner", 
                "api_key": "nexus_test_key_2024"
            }).execute()
            
        t_id = tenant_res.data[0]['id']

        # Registrazione azienda
        comp_res = supabase.table("companies").upsert({
            "company_name": company_name,
            "tenant_id": t_id
        }, on_conflict="company_name").execute()
        c_id = comp_res.data[0]['id']

        # Registrazione Analisi
        supabase.table("credit_analyses").insert({
            "company_id": c_id,
            "dscr_value": metrics['dscr'],
            "leverage_value": metrics['leverage'],
            "rating_code": decision['score'],
            "decision_output": decision['decision']
        }).execute()
        return True
    except Exception as e:
        st.error(f"Errore Tecnico Database: {e}")
        return False

# --- UI STREAMLIT ---
st.title("🏛️ Coin-Nexus | Credit Decision Engine")

tab1, tab2 = st.tabs(["📊 Terminale", "📜 Storico Analisi"])

with tab1:
    col_input, col_viz = st.columns([1, 2])
    
    with col_input:
        st.subheader("Dati Input")
        name = st.text_input("Ragione Sociale", "Azienda Beta Srl")
        rev = st.number_input("Ricavi (€)", value=1500000)
        ebitda = st.number_input("EBITDA (€)", value=300000)
        debt = st.number_input("Debito Totale (€)", value=450000)
        
        if st.button("ESEGUI E SALVA AUDIT"):
            # Esecuzione calcoli dal file engine/scoring.py
            m = calculate_metrics({"revenue": rev, "ebitda": ebitda, "debt": debt})
            d = get_credit_decision(m)
            
            if push_to_db(name, m, d):
                st.success("✅ Analisi salvata con successo!")
                st.session_state['last_res'] = (m, d, name)

    with col_viz:
        if 'last_res' in st.session_state:
            m, d, n = st.session_state['last_res']
            st.subheader(f"Dossier: {n}")
            
            c1, c2 = st.columns(2)
            c1.metric("Rating", d['score'])
            c2.metric("Decisione", d['decision'])
            
            # Grafico Gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number", 
                value=m['dscr'],
                title={'text': "DSCR (Capacità di Rimborso)"},
                gauge={'axis': {'range': [0, 5]},
                       'bar': {'color': d['color']},
                       'steps': [
                           {'range': [0, 1.2], 'color': "lightgray"},
                           {'range': [1.2, 5], 'color': "white"}
                       ]}))
            fig.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("📑 Database Audit Log")
    if st.button("Aggiorna Storico"):
        res = supabase.table("credit_analyses").select("created_at, rating_code, decision_output, companies(company_name)").order("created_at", desc=True).execute()
        if res.data:
            df = pd.json_normalize(res.data)
            # Rinominiamo le colonne per renderle leggibili
            df.columns = ['Data', 'Rating', 'Decisione', 'Nome Azienda']
            st.dataframe(df, use_container_width=True)
