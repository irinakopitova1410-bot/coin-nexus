import streamlit as st
from supabase import create_client, Client
from scoring import NexusScorer
import plotly.graph_objects as go

# Connessione a Supabase
url = st.secrets["https://ipmttldwfsxuubugiyir.supabase.co"]
key = st.secrets["sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Coin-Nexus SaaS", layout="wide")

# --- LOGICA DI AUTENTICAZIONE ---
if 'user' not in st.session_state:
    st.session_state.user = None

def login():
    with st.sidebar:
        st.subheader("🔐 Accesso Area Riservata")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Accedi"):
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state.user = res.user
            st.rerun()
        if st.button("Registrati"):
            supabase.auth.sign_up({"email": email, "password": password})
            st.info("Controlla la mail per confermare!")

# --- INTERFACCIA PRINCIPALE ---
if st.session_state.user is None:
    st.title("🏛️ Benvenuto in Coin-Nexus")
    st.warning("Effettua il login per accedere al terminale di scoring e ai tuoi dati salvati.")
    login()
else:
    st.sidebar.success(f"Connesso come: {st.session_state.user.email}")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    st.title("🏛️ Coin-Nexus | Enterprise Terminal")
    
    # Area Input
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        company = st.text_input("Ragione Sociale")
        rev = st.number_input("Ricavi (€)", value=1000000)
    with col_in2:
        costs = st.number_input("Costi (€)", value=800000)
        debt = st.number_input("Debito (€)", value=200000)

    if st.button("🚀 ESEGUI AUDIT & SALVA NEL CLOUD"):
        scorer = NexusScorer(rev, costs, debt)
        rating, desc = scorer.get_nexus_rating()
        
        # Salvataggio su Database
        data = {
            "user_id": st.session_state.user.id,
            "company_name": company,
            "rating": rating,
            "revenue": rev
        }
        supabase.table("audit_reports").insert(data).execute()
        st.success(f"Report per {company} salvato correttamente!")
        
        # Qui metti i tuoi grafici professionali...
        st.metric("Rating", rating, desc)

    # --- STORICO DATI ---
    st.divider()
    st.subheader("📑 I tuoi Audit precedenti")
    history = supabase.table("audit_reports").select("*").execute()
    if history.data:
        st.table(history.data)
