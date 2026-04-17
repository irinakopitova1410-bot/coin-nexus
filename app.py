import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
from supabase import create_client, Client
import datetime
import io

# --- 1. CONFIGURAZIONE ---
st.set_page_config(page_title="Nexus Enterprise | SaaS Hub", layout="wide", page_icon="🏛️")

@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["https://ipmttldwfsxuubugiyir.supabase.co"]
        key = st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlwbXR0bGR3ZnN4dXVidWdpeWlyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjA5NDE3MSwiZXhwIjoyMDkxNjcwMTcxfQ.hFsH0_JtDOTgsPUm-RhvcZRztXqQmafaHgfMN6WxcKk"]
        return create_client(url, key)
    except:
        return None

supabase = init_supabase()

# --- 2. LOGICA DI AUTENTICAZIONE IBRIDA ---
def login_logic(email_input, pwd_input):
    # --- ADMIN PROVVISORIO (BACKDOOR) ---
    # Cambia queste due stringhe con la mail e pass che vuoi usare tu per i test
    ADMIN_MAIL = "admin@test.it" 
    ADMIN_PASS = "nexus2026"

    if email_input == ADMIN_MAIL and pwd_input == ADMIN_PASS:
        return {"email": ADMIN_MAIL, "role": "admin"}
    
    # --- LOGIN STANDARD TRAMITE SUPOBASE ---
    if supabase:
        try:
            res = supabase.auth.sign_in_with_password({"email": email_input, "password": pwd_input})
            if res:
                return {"email": res.user.email, "role": "user"}
        except:
            return None
    return None

# --- 3. MOTORE ANALISI ENTERPRISE ---
def run_enterprise_analysis(rev, ebitda, debt):
    rev = max(rev, 1)
    eb_val = max(ebitda, 1)
    db_val = max(debt, 1)
    z = (1.2 * (rev*0.1/db_val)) + (3.3 * (eb_val/db_val))
    pd_rate = max(0.005, min(0.99, 1 / (1 + (z**2.5)))) 
    ead = rev * 0.15 
    expected_loss = ead * pd_rate * 0.45 
    suggested_rate = (0.04 + pd_rate + 0.03) * 100 
    
    status = "SOLIDO" if z > 2.6 else "VULNERABILE" if z > 1.1 else "DISTRESSED"
    color = "#00CC66" if z > 2.6 else "#FFA500" if z > 1.1 else "#FF4B4B"
    
    return {
        "z": z, "status": status, "color": color, 
        "pd": pd_rate * 100, "el": expected_loss, "rate": suggested_rate,
        "ros": (eb_val/rev)*100, "lev": debt/eb_val
    }

# --- 4. SCHERMATA LOGIN ---
if 'auth_user' not in st.session_state:
    st.session_state.auth_user = None

if st.session_state.auth_user is None:
    st.title("🏛️ Nexus Enterprise | Login")
    email = st.text_input("Email")
    pwd = st.text_input("Password", type="password")
    
    if st.button("Accedi al Sistema", use_container_width=True):
        user_data = login_logic(email, pwd)
        if user_data:
            st.session_state.auth_user = user_data
            st.success(f"Benvenuto {user_data['email']}!")
            st.rerun()
        else:
            st.error("Credenziali non valide.")
    st.stop()

# --- 5. DASHBOARD POST-LOGIN ---
with st.sidebar:
    st.title("🏛️ Nexus System")
    st.write(f"👤 **Sessione:** {st.session_state.auth_user['email']}")
    
    if st.session_state.auth_user['role'] == "admin":
        st.success("⚡ MODO AMMINISTRATORE")
    
    if st.button("Logout"):
        st.session_state.auth_user = None
        st.rerun()
    
    st.divider()
    uploaded_file = st.file_uploader("📂 Carica Bilancio ERP", type=["xlsx", "csv"])
    nome_az = st.text_input("Azienda", "Target S.p.A.")
    rev_in = st.number_input("Fatturato (€)", value=1500000)
    ebit_in = st.number_input("EBITDA (€)", value=250000)
    pfn_in = st.number_input("Debito (€)", value=500000)

st.title("🕵️ Credit Risk & Enterprise Intelligence")

if st.button("🚀 ESEGUI ANALISI GLOBALE", use_container_width=True):
    res = run_enterprise_analysis(rev_in, ebit_in, pfn_in)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div style='background:{res['color']};padding:25px;border-radius:15px;text-align:center;color:white;'><h2>{res['status']}</h2></div>", unsafe_allow_html=True)
    c2.metric("Altman Z-Score", f"{res['z']:.2f}")
    c3.metric("Leva Finanziaria", f"{res['lev']:.2f}x")

    st.divider()
    st.subheader("🎯 Metriche Basilea IV (Credit Risk)")
    m1, m2, m3 = st.columns(3)
    m1.metric("Perdita Attesa (EL)", f"€ {res['el']:,.0f}")
    m2.metric("Probabilità Default", f"{res['pd']:.2f}%")
    m3.metric("Pricing Credito", f"{res['rate']:.2f}%")
    # FUNZIONE SOLO PER ADMIN
    if st.session_state.auth_user['role'] == "admin":
        st.divider()
        st.subheader("📜 Admin Panel - Data Logs")
        st.json(res)
# --- COLLEGAMENTO REALE AL MOTORE SU RENDER ---
# --- INIZIO NEXUS PARTNER DASHBOARD (Incolla in fondo al file) ---
# --- NEXUS PARTNER DASHBOARD DEFINITIVA ---
if st.session_state.auth_user['role'] == "admin":
    st.divider()
    st.header("📊 Nexus Partner Dashboard")
    
    # Verifichiamo se i Secrets sono presenti
    if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
        try:
            from supabase import create_client
            import pandas as pd

            # Leggiamo dai Secrets (assicurati di averli salvati nella dashboard di Streamlit!)
            s_url = st.secrets["https://ipmttldwfsxuubugiyir.supabase.co"]
            s_key = st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlwbXR0bGR3ZnN4dXVidWdpeWlyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjA5NDE3MSwiZXhwIjoyMDkxNjcwMTcxfQ.hFsH0_JtDOTgsPUm-RhvcZRztXqQmafaHgfMN6WxcKk"]
            supabase_client = create_client(s_url, s_key)

            # 1. Recupero Crediti Residui
            t_res = supabase_client.table("tenants").select("name, credit_balance").eq("api_key", "nexus_test_key_2026").execute()
            
            if t_res.data:
                info = t_res.data[0]
                c1, c2 = st.columns(2)
                c1.metric("Partner Attivo", info['name'])
                c2.metric("Crediti Disponibili", f"{info['credit_balance']} / 5000")

            # 2. Visualizzazione Log Ultime Analisi
            st.subheader("📜 Registro Operazioni Integrato")
            l_res = supabase_client.table("analysis_logs").select("created_at, company_name, z_score").order("created_at", desc=True).limit(5).execute()
            
            if l_res.data:
                df_logs = pd.DataFrame(l_res.data)
                df_logs.columns = ['Data/Ora', 'Azienda Analizzata', 'Z-Score']
                st.dataframe(df_logs, use_container_width=True)
            else:
                st.info("In attesa della prima analisi per popolare i log.")

        except Exception as e:
            st.error(f"Errore di connessione a Supabase: {e}")
    else:
        # Questo è il messaggio che vedi ora. Sparirà appena i Secrets saranno salvati correttamente.
        st.warning("⚠️ Configurazione Supabase non trovata nei Secrets di Streamlit.")
