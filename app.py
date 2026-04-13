import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime
from sklearn.ensemble import IsolationForest
from supabase import create_client, Client

# --- CONFIGURAZIONE SUPABASE ---
SUPABASE_URL = "https://ipmttldwfsxuubugiyir.supabase.co"
# Incolla qui la tua chiave 'anon' 'public' che hai appena copiato da Supabase
SUPABASE_KEY = "sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos" 

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Errore connessione Database: {e}")

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="COIN-NEXUS QUANTUM AI", layout="wide", page_icon="💠")

# --- 2. SISTEMA DI ACCESSO ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown("<h1 style='text-align: center; color: #00f2ff;'>💠 COIN-NEXUS PLATINUM</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='background: rgba(10,20,40,0.8); padding:20px; border-radius:10px; border:1px solid #00f2ff'>", unsafe_allow_html=True)
        pwd = st.text_input("CHIAVE DI LICENZA CLOUD", type="password")
        if st.button("SBLOCCA SISTEMA"):
            if pwd == "PLATINUM2026":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Accesso negato.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 3. LOGICA DI RATING ---
def analizza_solvibilita(df, col_val):
    totale = df[col_val].sum()
    score = np.random.uniform(0.4, 0.9) # Simulazione AI Rating
    if score > 0.7: return "ALTA SOLVIBILITÀ (Rating A)", "🟢"
    if score > 0.4: return "SOLVIBILE (Rating B)", "🟡"
    return "RISCHIO (Rating C)", "🔴"

# --- 4. INTERFACCIA ---
st.title("💠 COIN-NEXUS QUANTUM AI v3.5")

with st.sidebar:
    st.header("⚙️ CONFIGURAZIONE")
    studio = st.text_input("STUDIO/BANCA", "PLATINUM_REVISION_H")
    file = st.file_uploader("CARICA BILANCIO (Excel/CSV)", type=['xlsx', 'csv'])
    if st.button("LOGOUT"):
        st.session_state["authenticated"] = False
        st.rerun()

if file:
    try:
        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        num_col = df.select_dtypes(include=[np.number]).columns[0]
        massa = df[num_col].sum()
        rating_label, icona = analizza_solvibilita(df, num_col)

        # Dashboard
        c1, c2 = st.columns(2)
        c1.metric("MASSA RICAVI", f"€{massa:,.2f}")
        c2.metric("ESITO RATING", rating_label)

        if st.button("💾 SALVA REPORT SU SUPABASE"):
            data = {"studio_nome": studio, "massa_totale": float(massa), "rating": rating_label}
            supabase.table("reports").insert(data).execute()
            st.success("Dati sincronizzati con successo!")

        st.plotly_chart(px.histogram(df, x=num_col, template="plotly_dark"), use_container_width=True)
        
        # Storico
        st.divider()
        st.subheader("📁 Storico Ultime Analisi (Cloud)")
        res = supabase.table("reports").select("*").order("created_at", desc=True).limit(5).execute()
        if res.data:
            st.dataframe(pd.DataFrame(res.data)[["created_at", "studio_nome", "rating", "massa_totale"]])

    except Exception as e:
        st.error(f"Errore: {e}")
