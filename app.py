import streamlit as st
import plotly.graph_objects as go
from supabase import create_client
import pandas as pd
import json

# --- 1. CONFIGURAZIONE ---
st.set_page_config(page_title="Coin-Nexus Enterprise", layout="wide")

@st.cache_resource
def init_db():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except:
        return None

db = init_db()

# --- 2. LOGICA DI CALCOLO ---
def process_data(data):
    try:
        r = float(data.get('revenue', 0))
        e = float(data.get('ebitda', 0))
        d = float(data.get('debt', 1))
        dscr = e / d
        score = "AAA" if dscr > 2.2 else "BBB" if dscr > 1.2 else "CCC"
        return {"score": score, "dscr": dscr, "ebitda": e, "rev": r}
    except:
        return None

# --- 3. UI PRINCIPALE ---
st.title("🏛️ Coin-Nexus | Enterprise Risk Engine")

# QUI CREIAMO I TAB (Appariranno sotto il titolo)
tab1, tab2 = st.tabs(["📊 Terminale Analisi", "🔌 ERP Connect (JSON)"])

with tab1:
    col_side, col_main = st.columns([1, 3])
    
    with col_side:
        st.header("Input Manuale")
        name = st.text_input("Azienda", "Target Srl")
        r_in = st.number_input("Ricavi", value=1000000)
        e_in = st.number_input("EBITDA", value=200000)
        d_in = st.number_input("Debito", value=150000)
        run = st.button("ESEGUI ANALISI")

    with col_main:
        if run:
            res = process_data({'revenue': r_in, 'ebitda': e_in, 'debt': d_in})
            if res:
                st.subheader(f"Risultati per: {name}")
                m1, m2, m3 = st.columns(3)
                m1.metric("Rating", res['score'])
                m2.metric("DSCR", f"{res['dscr']:.2f}")
                m3.metric("EBITDA", f"€{res['ebitda']:,.0f}")
                
                fig = go.Figure(go.Indicator(mode="gauge+number", value=res['dscr'], 
                                gauge={'axis':{'range':[0,5]}, 'steps':[{'range':[0,1.2],'color':"red"},{'range':[1.2,5],'color':"green"}]}))
                fig.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)', font={'color':"white"})
                st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("🔌 Gateway Integrazione Dati")
    st.write("Incolla qui il JSON generato dal tuo ERP per un'analisi automatica.")
    
    sample_json = {
        "azienda": "Global Export Spa",
        "revenue": 2500000,
        "ebitda": 450000,
        "debt": 350000
    }
    
    json_input = st.text_area("Incolla JSON", value=json.dumps(sample_json, indent=2), height=200)
    
    if st.button("Analizza Dati ERP"):
        try:
            parsed = json.loads(json_input)
            res = process_data(parsed)
            st.success(f"Dati di {parsed.get('azienda')} elaborati!")
            st.json(res)
        except:
            st.error("Errore nel formato JSON")

# --- 4. STORICO DATABASE ---
st.divider()
st.subheader("📑 Ultime Analisi Cloud")
if db:
    try:
        raw = db.table("audit_reports").select("company_name,rating,created_at").order("created_at",desc=True).limit(5).execute()
        if raw.data:
            st.dataframe(pd.DataFrame(raw.data), use_container_width=True)
    except:
        st.info("Database pronto per ricevere dati.")
