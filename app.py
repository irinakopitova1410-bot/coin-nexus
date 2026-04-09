import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAZIONE
st.set_page_config(page_title="Coin-Nexus Elite", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { background-color: #0f172a; color: white; }
    .metric-card { background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 15px; }
    #MainMenu, header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("COIN-NEXUS ELITE")
st.caption("Intelligence Finanziaria & Gestione Rischi")

# --- KPI FISSI ---
k1, k2, k3, k4 = st.columns(4)
k1.metric("Acquisti Mese", "€ 27.450", "+5.2%")
k2.metric("Richieste SAP", "2 Pendenti")
k3.metric("Stock Acciaio", "SOTTOSCORTA", "-12%", delta_color="inverse")
k4.metric("Scadenze Docfinance", "€ 13.400")

st.markdown("---")
st.header("🛡️ Analisi Solvibilità")

uploaded_file = st.file_uploader("Carica Bilancio (CSV o Excel)", type=["csv", "xlsx"])

# Inizializzazione variabili di sicurezza
liq_val, solv_val, stato_rischio, color_border = 0.0, 0.0, "ATTESA DATI", "#94a3b8"
df_bil = None 

if uploaded_file:
    try:
        # Lettura
        if uploaded_file.name.endswith('.csv'):
            try:
                df_bil = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='utf-8')
            except:
                uploaded_file.seek(0)
                df_bil = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='ISO-8859-1')
        else:
            df_bil = pd.read_excel(uploaded_file)
        
        # Pulizia nomi colonne (rimuove spazi extra)
        df_bil.columns = df_bil.columns.str.strip()

        # Controllo se le colonne esistono
        possibili_cat = [c for c in df_bil.columns if 'Categoria' in c or 'Voce' in c]
        possibili_val = [c for c in df_bil.columns if 'Valore' in c or 'Importo' in c]

        if possibili_cat and possibili_val:
            col_cat = possibili_cat[0]
            col_val = possibili_val[0]

            # Calcoli
            def get_val(label):
                return df_bil[df_bil[col_cat].str.contains(label, na=False, case=False)][col_val].sum()

            a_corr = get_val('Attività Correnti')
            p_corr = get_val('Passività Correnti')
            patrim = get_val('Patrimonio Netto')
            p_tot = get_val('Passività')

            liq_val = round(a_corr / p_corr, 2) if p_corr > 0 else 0.0
            solv_val = round(patrim / p_tot, 2) if p_tot > 0 else 0.0
            
            stato_rischio = "BASSO" if liq_val > 1.2 else "CRITICO"
            color_border = "#10b981" if liq_val > 1.2 else "#ef4444"
            st.success("✅ Dati analizzati")
        else:
            st.error("⚠️ Errore: Il file deve avere le colonne 'Categoria' e 'Valore'")
            df_bil = None # Reset per non far scattare il grafico

    except Exception as e:
        st.error(f"Errore tecnico: {e}")
        df_bil = None

# --- CARD ---
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="metric-card" style="border-top: 5px solid {color_border}"><strong>LIQUIDITÀ</strong><h2>{liq_val}</h2></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card" style="border-top: 5px solid #3b82f6;"><strong>SOLVIBILITÀ</strong><h2>{solv_val}</h2></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card" style="border-top: 5px solid {color_border}"><strong>RISCHIO</strong><h2>{stato_rischio}</h2></div>', unsafe_allow_html
