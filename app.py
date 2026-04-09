import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAZIONE PAGINA (Deve essere la PRIMA istruzione Streamlit)
st.set_page_config(page_title="Coin-Nexus Elite", layout="wide", initial_sidebar_state="collapsed")

# 2. STILE CSS
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: white; }
    .metric-card {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #334155;
        margin-bottom: 10px;
    }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("COIN-NEXUS ELITE")
st.caption("Sistema Gestionale Riservato | Analisi Solvibilità")

# --- DATABASE INTERNO ---
data = {
    'ID': ['REQ-9901', 'PAY-4402', 'STK-1105', 'REQ-9905', 'PAY-4409'],
    'Sistema': ['SAP', 'Docfinance', 'SO99+', 'SAP', 'Docfinance'],
    'Stato': ['In Approvazione', 'In Attesa', 'CRITICO', 'Spedito', 'Da Pagare'],
    'Valore': [15000, 4500, 0, 12000, 8900]
}
df_op = pd.DataFrame(data)

# --- KPI SUPERIORI ---
k1, k2, k3 = st.columns(3)
k1.metric("Acquisti Totali", "€ 27.000", "+5.2%")
k2.metric("Richieste SAP", "2 REQ", "In approvazione")
k3.metric("Rischio Stock", "CRITICO", "Acciaio", delta_color="inverse")

st.markdown("---")

# --- SEZIONE CARICAMENTO BILANCIO ---
st.header("🛡️ Analisi Solvibilità e Rischi")
uploaded_file = st.file_uploader("Carica Bilancio (CSV o Excel)", type=["csv", "xlsx"])

# Valori di default
liq_val, solv_val, stato_rischio, color_border = 0.0, 0.0, "ATTESA DATI", "#94a3b8"

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_bil = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='latin1')
        else:
            df_bil = pd.read_excel(uploaded_file)
        
        # Calcolo Indici (Cerca colonne 'Categoria' e 'Valore')
        if 'Categoria' in df_bil.columns and 'Valore' in str(df_bil.columns):
            # Identifica la colonna valore (gestisce nomi con simboli come €)
            col_val = [c for c in df_bil.columns if 'Valore' in c][0]
            
            attivo = df_bil[df_bil['Categoria'].str.contains('Attività Correnti', na=False)][col_val].sum()
            passivo = df_bil[df_bil['Categoria'].str.contains('Passività Correnti', na=False)][col_val].sum()
            patrimonio = df_bil[df_bil['Categoria'].str.contains('Patrimonio Netto', na=False)][col_val].sum()
            debiti = df_bil[df_bil['Categoria'].str.contains('Passività', na=False)][col_val].sum()

            liq_val = round(attivo / passivo, 2) if passivo > 0 else 0.0
            solv_val = round(patrimonio / debiti, 2) if debiti > 0 else 0.0
            
            stato_rischio = "BASSO" if liq_val > 1.2 else "ALTO"
            color_border = "#10b981" if liq_val > 1.2 else "#ef4444"
            st.success("✅ Bilancio caricato!")
    except Exception as e:
        st.error(f"Errore lettura file: {e}")

# CARD RISULTATI
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="metric-card" style="border-top:5px solid {color_border}"><strong>LIQUIDITÀ</strong><h2>{liq_val}</h2></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card"
