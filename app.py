import streamlit as st
import plotly.graph_objects as go
from supabase import create_client
import pandas as pd
import json

# --- SETUP ---
st.set_page_config(page_title="Coin-Nexus SaaS", layout="wide")

@st.cache_resource
def init_db():
    try: return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except: return None

db = init_db()

def process_data(data):
    try:
        r = float(data.get('revenue', 0))
        e = float(data.get('ebitda', 0))
        d = float(data.get('debt', 1))
        dscr = e / d
        score = "AAA" if dscr > 2.2 else "BBB" if dscr > 1.2 else "CCC"
        return {"score": score, "dscr": dscr, "ebitda": e, "rev": r}
    except: return None

# --- UI ---
st.title("🏛️ Coin-Nexus | Risk Intelligence")

# Tab centrali
t1, t2 = st.tabs(["📊 Dashboard Manuale", "🔌 ERP Gateway (JSON)"])

with t1:
    col_s, col_m = st.columns([1, 2])
    with col_s:
        st.subheader("Parametri")
        n = st.text_input("Ragione Sociale", "Azienda srl")
        r = st.number_input("Fatturato", value=1000000)
        e = st.number_input("MOL (EBITDA)", value=250000)
        d = st.number_input("Debito Finanziario", value=400000)
        if st.button("ANALIZZA ORA"):
            st.session_state.res = process_data({'revenue': r, 'ebitda': e, 'debt': d})
            st.session_state.name = n

    with col_m:
        if 'res' in st.session_state:
            st.metric("Rating Aziendale", st.session_state.res['score'])
            fig = go.Figure(go.Indicator(mode="gauge+number", value=st.session_state.res['dscr'],
                gauge={'axis':{'range':[0,5]}, 'bar':{'color':"#00f2ff"}, 'steps':[{'range':[0,1.2],'color':"red"},{'range':[1.2,5],'color':"green"}]}))
            fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', font={'color':"white"})
            st.plotly_chart(fig, use_container_width=True)

with t2:
    st.subheader("🔌 ERP Real-Time Integration")
    st.write("Incolla il JSON per bypassare l'input manuale.")
    area = st.text_area("JSON Payloads", height=200, placeholder="Incolla qui...")
    if st.button("Sincronizza e Analizza"):
        try:
            parsed = json.loads(area)
            res = process_data(parsed)
            st.success(f"Dati ricevuti per {parsed.get('azienda', 'N/A')}")
            st.json(res)
            if db:
                db.table("audit_reports").insert({"company_name": parsed.get('azienda'), "rating": res['score'], "revenue": res['rev']}).execute()
        except Exception as err:
            st.error(f"Errore: {err}")

# --- ARCHIVIO ---
st.divider()
if db:
    try:
        raw = db.table("audit_reports").select("company_name,rating,created_at").order("created_at",desc=True).limit(5).execute()
        if raw.data: st.dataframe(pd.DataFrame(raw.data), use_container_width=True)
    except: pass
