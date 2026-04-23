import streamlit as st
import pandas as pd
import requests
from supabase import create_client
import datetime

# --- CONFIG PAGINA ---
st.set_page_config(
    page_title="Nexus Enterprise | SaaS Hub",
    layout="wide",
    page_icon="🏛️"
)

# --- INIT SUPABASE SICURO ---
@st.cache_resource
def init_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_ANON_KEY"]
    )

supabase = init_supabase()

# --- AUTH SICURA SOLO SUPABASE ---
def login(email, password):
    try:
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return res.user if res else None
    except:
        return None

# --- SESSION ---
if "user" not in st.session_state:
    st.session_state.user = None

# --- LOGIN PAGE ---
if not st.session_state.user:
    st.title("🏛️ Nexus Enterprise | Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        user = login(email, password)
        if user:
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Credenziali non valide")

    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏛️ Nexus System")
    st.write(f"👤 {st.session_state.user.email}")

    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()

    st.divider()

    st.subheader("Dati Azienda")
    nome_az = st.text_input("Ragione Sociale", "Target S.p.A.")
    revenue = st.number_input("Fatturato (€)", value=1500000.0)
    ebitda = st.number_input("EBITDA (€)", value=250000.0)
    debt = st.number_input("Debito (€)", value=500000.0)

# --- MAIN ---
st.title("🕵️ Credit Risk & Enterprise Intelligence")

# --- API CONFIG ---
API_URL = st.secrets["https://ipmttldwfsxuubugiyir.supabase.co"]
API_KEY = st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlwbXR0bGR3ZnN4dXVidWdpeWlyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYwOTQxNzEsImV4cCI6MjA5MTY3MDE3MX0.HRFDqEKVCygVSKByVupgK3XGIkkpxxCyO7PH4LucPZg"]

payload = {
    "company_name": nome_az,
    "revenue": float(revenue),
    "ebitda": float(ebitda),
    "total_debt": float(debt)
}

st.code(payload, language="json")

# --- CALL API ---
if st.button("🚀 Analizza", use_container_width=True):

    headers = {
        "x-api-key": API_KEY
    }

    with st.spinner("Analisi in corso..."):
        try:
            res = requests.post(API_URL, json=payload, headers=headers)

            if res.status_code == 200:
                data = res.json()

                c1, c2, c3 = st.columns(3)
                c1.metric("Z-Score", data["results"]["score"])
                c2.metric("Rating", data["results"]["rating"])
                c3.metric("Crediti Residui", data["results"]["credits_left"])

                st.success("Analisi completata")
            else:
                st.error(f"Errore API: {res.text}")

        except Exception as e:
            st.error("Errore di connessione")

# --- DASHBOARD DATI ---
st.divider()
st.subheader("📊 Storico Analisi")

try:
    logs = supabase.table("analysis_logs") \
        .select("company_name, z_score, created_at") \
        .order("created_at", desc=True) \
        .limit(10) \
        .execute()

    if logs.data:
        df = pd.DataFrame(logs.data)
        st.dataframe(df, use_container_width=True)

except:
    st.warning("Nessun dato disponibile")
