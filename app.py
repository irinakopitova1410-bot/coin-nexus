import streamlit as st
import plotly.graph_objects as go
from supabase import create_client
import pandas as pd
from fpdf import FPDF

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Coin-Nexus Enterprise", layout="wide")

@st.cache_resource
def init_db():
    try: return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except: return None

db = init_db()

# --- LOGICA DI ELABORAZIONE DATI (INGESTION) ---
def process_raw_data(data):
    """Pulisce e valida i dati provenienti da ERP o Manuali"""
    try:
        r = float(data.get('revenue', 0))
        e = float(data.get('ebitda', 0))
        d = float(data.get('debt', 1)) # Evita divisione per zero
        dscr = e / d
        score = "AAA" if dscr > 2.2 else "BBB" if dscr > 1.2 else "CCC"
        return {"score": score, "dscr": dscr, "ebitda": e}
    except: return None

# --- UI PRINCIPALE ---
st.title("🏛️ Coin-Nexus | Enterprise Risk Engine")

tab1, tab2 = st.tabs(["📊 Terminale", "🔌 ERP Connect"])

with tab1:
    with st.sidebar:
        st.header("Input Manuale")
        name = st.text_input("Azienda", "Target Srl")
        r = st.number_input("Ricavi", value=1000000)
        e = st.number_input("EBITDA", value=200000)
        d = st.number_input("Debito", value=150000)
        run = st.button("ESEGUI ANALISI")

    if run:
        res = process_raw_data({'revenue': r, 'ebitda': e, 'debt': d})
        if res:
            st.subheader(f"Analisi Asset: {name}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Rating", res['score'])
            c2.metric("DSCR", f"{res['dscr']:.2f}")
            c3.metric("Margine Operativo", f"€{res['ebitda']:,.0f}")
            
            # Grafico Professionale
            fig = go.Figure(go.Indicator(mode="gauge+number", value=res['dscr'], 
                            gauge={'axis':{'range':[0,5]}, 'steps':[{'range':[0,1.2],'color':"red"},{'range':[1.2,5],'color':"green"}]}))
            fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', font={'color':"white"})
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.info("Endpoint API: `https://coin-nexus.streamlit.app/v1/ingest` (Simulato)")
    st.write("In questa sezione configurerai i **Webhook** per ricevere i dati direttamente dal tuo software gestionale.")
    if st.button("Simula Ricezione Dati ERP"):
        st.toast("Dati ricevuti da ERP esterno...", icon="🔌")
        st.success("Analisi completata per: 'Global Export Spa' (Dati da SAP)")

# --- FOOTER CLOUD ---
if db:
    st.divider()
    try:
        raw = db.table("audit_reports").select("company_name,rating,created_at").order("created_at",desc=True).limit(5).execute()
        st.dataframe(pd.DataFrame(raw.data), use_container_width=True)
    except: st.write("Database pronto.")
