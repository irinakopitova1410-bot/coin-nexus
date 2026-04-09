import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAZIONE INTERFACCIA
st.set_page_config(page_title="Coin-Nexus Elite", layout="wide", initial_sidebar_state="collapsed")

# CSS per stile Dark ed eliminazione elementi standard
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: white; }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .metric-card {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #334155;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("COIN-NEXUS ELITE")
st.caption("Sistema Gestionale Riservato | Analisi Rischi e Solvibilità")

# --- DATABASE INTERNO (Dati Operativi) ---
data = {
    'ID_Operazione': ['REQ-9901', 'PAY-4402', 'STK-1105', 'REQ-9905', 'PAY-4409', 'PRAT-001'],
    'Sistema': ['SAP', 'Docfinance', 'SO99+', 'SAP', 'Docfinance', 'Telemaco'],
    'Descrizione': ['Acquisto Materie Prime', 'Saldi Fornitore X', 'Sottoscorta Acciaio', 'Ordine Cliente Y', 'Riba in Scadenza', 'Visura Camerale'],
    'Valore_Euro': [15000, 4500, 0, 12000, 8900, 50],
    'Stato': ['In Approvazione', 'In Attesa', 'CRITICO', 'Spedito', 'Da Pagare', 'Inviata']
}
df_operativo = pd.DataFrame(data)

# --- SEZIONE KPI OPERATIVI ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown('<div class="metric-card" style="border-left: 5px solid #3b82f6;"><p style="color: #94a3b8; font-size: 0.8rem; margin: 0;">TOTALE ACQUISTI</p><h2 style="margin: 0;">€ 27.000</h2></div>', unsafe_allow_html=True)
with kpi4:
    st.markdown('<div class="metric-card" style="border-left: 5px solid #f87171;"><p style="color: #94a3b8; font-size: 0.8rem; margin: 0;">ALLERTA STOCK</p><h2 style="margin: 0; color: #f87171;">CRITICO</h2></div>', unsafe_allow_html=True)

st.markdown("---")

# --- SEZIONE BILANCIO E RISCHI (RIGA 95) ---
st.header("🛡️ Analisi Solvibilità e Rischi")
uploaded_file = st.file_uploader("Carica il Bilancio (Excel o CSV)", type=["csv", "xlsx"])

# Inizializzazione variabili di default
liq_val, solv_val, stato_rischio, color_border = 0.95, 0.42, "ATTESA FILE", "#94a3b8"

if uploaded_file:
    try:
        # Lettura file
        if uploaded_file.name.endswith('.csv'):
            try:
                df_bil = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='utf-8')
            except:
                uploaded_file.seek(0)
                df_bil = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='ISO-8859-1')
        else:
            df_bil = pd.read_excel(uploaded_file)

        # Calcolo Indici (Cerca colonne 'Categoria' e 'Valore')
        if 'Categoria' in df_bil.columns and 'Valore (€)' in df_bil.columns:
            attivo = df_bil[df_bil['Categoria'].str.contains('Attività Correnti', na=False)]['Valore (€)'].sum()
            passivo = df_bil[df_bil['Categoria'].str.contains('Passività Correnti', na=False)]['Valore (€)'].sum()
            patrimonio = df_bil[df_bil['Categoria'].str.contains('Patrimonio Netto', na=False)]['Valore (€)'].sum()
            debiti = df_bil[df_bil['Categoria'].str.contains('Passività', na=False)]['Valore (€)'].sum()

            liq_val = round(attivo / passivo, 2) if passivo > 0 else 0.0
            solv_val = round(patrimonio / debiti, 2) if debiti > 0 else 0.0
            
            stato_rischio = "BASSO" if liq_val > 1.2 else "CRITICO"
            color_border = "#10b981" if liq_val > 1.2 else "#ef4444"
            st.success("✅ Bilancio analizzato con successo!")
        else:
            st.warning("⚠️ Il file deve contenere le colonne 'Categoria' e 'Valore (€)'")
    except Exception as e:
        st.error(f"Errore tecnico: {e}")

# Visualizzazione Card Finanziarie
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div style="background:#334155; padding:20px; border-radius:10px; border-left:5px solid {color_border};"><strong>LIQUIDITÀ</strong><h2>{liq_val}</h2></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div style="background:#334155; padding:20px; border-radius:10px; border-left:5px solid #3b82f6;"><strong>SOLVIBILITÀ</strong><h2>{solv_val}</h2></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div style="background:#451a1a; padding:20px; border-radius:10px; border-left:5px solid #ef4444;"><strong>RISCHIO</strong><h2>{stato_rischio}</h2></div>', unsafe_allow_html=True)

# Tabella Operazioni
st.markdown("### 📋 Registro Operazioni Correnti")
st.dataframe(df_operativo, use_container_width=True)
