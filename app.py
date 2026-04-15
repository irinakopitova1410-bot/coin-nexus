import streamlit as st
import plotly.graph_objects as go
from supabase import create_client, Client

# --- CONNESSIONE DATABASE ---
# Recupera le chiavi dai Secrets di Streamlit Cloud
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Errore di configurazione: controlla i Secrets su Streamlit Cloud.")
    st.stop()

# --- LOGICA DI SCORING ---
class NexusScorer:
    def __init__(self, revenue, costs, debt):
        self.revenue = float(revenue)
        self.costs = float(costs)
        self.debt = float(debt)
        self.ebitda = self.revenue - self.costs

    def get_nexus_rating(self):
        dscr = self.ebitda / (self.debt if self.debt > 0 else 1)
        score = ((self.ebitda / self.revenue) * 60) + (min(dscr, 5) * 8)
        if score > 75: return "AAA", "Massima Solvibilità"
        if score > 50: return "BBB", "Solvibilità Buona"
        return "CCC", "Rischio Monitorato"

# --- INTERFACCIA UI ---
st.set_page_config(page_title="Coin-Nexus SaaS", layout="wide")
st.title("🏛️ Coin-Nexus | Cloud Terminal")

with st.sidebar:
    st.header("📥 ERP Data Input")
    company = st.text_input("Ragione Sociale", "Azienda Esempio S.r.l.")
    rev = st.number_input("Ricavi (€)", value=1000000)
    costs = st.number_input("Costi (€)", value=800000)
    debt = st.number_input("Debito (€)", value=200000)
    run = st.button("🚀 ESEGUI & SALVA NEL CLOUD")

if run:
    scorer = NexusScorer(rev, costs, debt)
    rating, desc = scorer.get_nexus_rating()
    
    # SALVATAGGIO SU SUPABASE
    try:
        report_data = {
            "company_name": company,
            "rating": rating,
            "revenue": rev
        }
        supabase.table("audit_reports").insert(report_data).execute()
        st.success(f"Analisi di {company} salvata!")
    except Exception as e:
        st.error(f"Errore database: {e}")

    # RISULTATI VISIVI
    st.metric("Rating Basilea IV", rating, desc)
    fig = go.Figure(go.Scatterpolar(
        r=[80, 70, 90, 85, 75],
        theta=['Liquidità','Solvibilità','Efficienza','Resilienza','Rating'],
        fill='toself', line_color='cyan'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# --- VISUALIZZAZIONE DATABASE ---
st.divider()
st.subheader("📑 Database Storico Real-Time")
try:
    history = supabase.table("audit_reports").select("*").order("created_at", desc=True).execute()
    if history.data:
        st.dataframe(history.data, use_container_width=True)
except:
    st.info("In attesa del primo salvataggio...")
