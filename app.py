import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
from supabase import create_client, Client
import datetime
import io

# --- 1. CONFIGURAZIONE & CONNESSIONE ---
st.set_page_config(page_title="Nexus Enterprise | SaaS Hub", layout="wide", page_icon="🏛️")

@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error("Errore di connessione a Supabase. Controlla i Secrets.")
        return None

supabase = init_supabase()

# --- 2. GESTIONE AUTENTICAZIONE (SaaS Layer) ---
def login_user(email, password):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return res
    except Exception as e:
        st.error(f"Errore Login: {e}")
        return None

def register_user(email, password):
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        st.success("Registrazione effettuata! Controlla la mail per confermare (se attivo).")
        return res
    except Exception as e:
        st.error(f"Errore Registrazione: {e}")
        return None

# --- 3. MOTORE DI CALCOLO ENTERPRISE ---
def run_enterprise_analysis(rev, ebitda, debt):
    rev = max(rev, 1)
    eb_val = max(ebitda, 1)
    db_val = max(debt, 1)
    
    # Altman Z-Score & PD (Probabilità Default)
    z = (1.2 * (rev*0.1/db_val)) + (3.3 * (eb_val/db_val))
    pd_rate = max(0.005, min(0.99, 1 / (1 + (z**2.5)))) 
    
    # Expected Loss & Pricing (Basilea IV)
    ead = rev * 0.15 # Esposizione
    expected_loss = ead * pd_rate * 0.45 # LGD 45%
    suggested_rate = (0.04 + pd_rate + 0.03) * 100 # Costo + Rischio + Margine
    
    status = "SOLIDO" if z > 2.6 else "VULNERABILE" if z > 1.1 else "DISTRESSED"
    color = "#00CC66" if z > 2.6 else "#FFA500" if z > 1.1 else "#FF4B4B"
    
    return {
        "z": z, "status": status, "color": color, 
        "pd": pd_rate * 100, "el": expected_loss, "rate": suggested_rate,
        "ros": (eb_val/rev)*100, "lev": debt/eb_val, "ead": ead
    }

# --- 4. SCHERMATA DI ACCESSO (LOGIN/REGISTRAZIONE) ---
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("🏛️ Nexus Enterprise | Login")
    tab_log, tab_reg = st.tabs(["Accedi", "Registrati"])
    
    with tab_log:
        email = st.text_input("Email Aziendale")
        pwd = st.text_input("Password", type="password")
        if st.button("Entra nel Sistema"):
            session = login_user(email, pwd)
            if session:
                st.session_state.user = session.user
                st.rerun()
                
    with tab_reg:
        new_email = st.text_input("Nuova Email")
        new_pwd = st.text_input("Nuova Password", type="password")
        if st.button("Crea Account Enterprise"):
            register_user(new_email, new_pwd)
    st.stop()

# --- 5. DASHBOARD PRINCIPALE (SOLO PER LOGGATI) ---
with st.sidebar:
    st.title("🏛️ Nexus Control")
    st.write(f"👤 Utente: {st.session_state.user.email}")
    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()
    st.divider()
    
    # INPUT DATI
    uploaded_file = st.file_uploader("📂 Import ERP (Excel/CSV)", type=["xlsx", "csv"])
    nome_az = st.text_input("Azienda Target", "Nexus Demo S.p.A.")
    rev_in = st.number_input("Fatturato (€)", value=1500000)
    ebit_in = st.number_input("EBITDA (€)", value=250000)
    pfn_in = st.number_input("Debito Totale (€)", value=500000)

st.title("🕵️ Advanced Risk & Credit Intelligence")

if st.button("🚀 GENERA REPORT RISK-ADJUSTED", use_container_width=True):
    res = run_enterprise_analysis(rev_in, ebit_in, pfn_in)
    
    # VISUALIZZAZIONE RISULTATI
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div style='background:{res['color']};padding:25px;border-radius:15px;text-align:center;color:white;'><h2>{res['status']}</h2></div>", unsafe_allow_html=True)
    col2.metric("Altman Z-Score", f"{res['z']:.2f}")
    col3.metric("Leva Finanziaria", f"{res['lev']:.2f}x")

    st.divider()
    st.subheader("🎯 Metriche di Basilea IV (Pricing & Loss)")
    m1, m2, m3 = st.columns(3)
    m1.metric("Perdita Attesa (EL)", f"€ {res['el']:,.0f}")
    m2.metric("Probabilità Default", f"{res['pd']:.2f}%")
    m3.metric("Tasso Pricing Suggerito", f"{res['rate']:.2f}%")
    
    st.info(f"**Strategia Operativa:** Il tasso minimo di {res['rate']:.2f}% copre il rischio di perdita attesa di €{res['el']:,.0f}.")

    # PORTFOLIO RADAR (PER DOC FINANCE)
    st.divider()
    st.header("🛰️ Portfolio Risk Radar")
    portfolio_df = pd.DataFrame({
        'Azienda': [nome_az, 'Competitor A', 'Partner B'],
        'Score': [res['z'], 1.2, 2.9]
    })
    st.line_chart(portfolio_df.set_index('Azienda'))
