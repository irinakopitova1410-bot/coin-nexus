import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAZIONE (Deve essere la prima riga assoluta)
st.set_page_config(page_title="Coin-Nexus Elite", layout="wide", initial_sidebar_state="collapsed")

# 2. STILE CSS ELITE
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: white; }
    .metric-card { 
        background-color: #1e293b; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #334155; 
        margin-bottom: 15px; 
    }
    #MainMenu, header, footer {visibility: hidden;}
    .stTable { background-color: #1e293b; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("COIN-NEXUS ELITE")
st.caption("Intelligence Finanziaria & Gestione Rischi | Sistema Integrato")

# --- SEZIONE 1: KPI OPERATIVI ---
k1, k2, k3, k4 = st.columns(4)
k1.metric("Acquisti Mese", "€ 27.450", "+5.2%")
k2.metric("Richieste SAP", "2 Pendenti", "In approvazione")
k3.metric("Stock Acciaio", "SOTTOSCORTA", "-12%", delta_color="inverse")
k4.metric("Scadenze Docfinance", "€ 13.400", "Settimana prox")

st.markdown("---")

# --- SEZIONE 2: UPLOAD E ANALISI ROBUSTA ---
st.header("🛡️ Analisi Solvibilità e Bilancio")
uploaded_file = st.file_uploader("Carica Bilancio (CSV o Excel)", type=["csv", "xlsx"])

# Inizializzazione variabili di sicurezza
liq_val, solv_val, stato_rischio, color_border = 0.0, 0.0, "ATTESA DATI", "#94a3b8"
df_bil = None

if uploaded_file:
    try:
        # Lettura file con protezione per righe sporche (errore riga 7)
        if uploaded_file.name.endswith('.csv'):
            try:
                # Prova UTF-8, salta righe con troppe colonne, rileva separatore
                df_bil = pd.read_csv(uploaded_file, sep=None, engine='python', on_bad_lines='skip', encoding='utf-8')
            except:
                uploaded_file.seek(0)
                df_bil = pd.read_csv(uploaded_file, sep=None, engine='python', on_bad_lines='skip', encoding='latin1')
        else:
            df_bil = pd.read_excel(uploaded_file)
        
        # Pulizia nomi colonne
        df_bil.columns = df_bil.columns.str.strip()

        # Ricerca colonne Categoria e Valore
        poss_cat = [c for c in df_bil.columns if 'Categoria' in c or 'Voce' in c]
        poss_val = [c for c in df_bil.columns if 'Valore' in c or 'Importo' in c]

        if poss_cat and poss_val:
            c_cat, c_val = poss_cat[0], poss_val[0]
            
            # Funzione di calcolo sicura
            def get_v(label):
                mask = df_bil[c_cat].str.contains(label, na=False, case=False)
                return pd.to_numeric(df_bil[mask][c_val], errors='coerce').sum()

            a_corr = get_v('Attività Correnti')
            p_corr = get_v('Passività Correnti')
            patrim = get_v('
