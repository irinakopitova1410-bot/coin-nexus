import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAZIONE (Deve essere la prima riga)
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

# Inizializzazione variabili
liq_val, solv_val, stato_rischio, color_border = 0.0, 0.0, "ATTESA DATI", "#94a3b8"
df_bil = None 

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            try:
                df_bil = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='utf-8')
            except:
                uploaded_file.seek(0)
                df_bil = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='ISO-8859-1')
        else:
            df_bil = pd.read_excel(uploaded_file)
        
        df_bil.columns = df_bil.columns.str.strip()
        poss_cat = [c for c in df_bil.columns if 'Categoria' in c or 'Voce' in c]
        poss_val = [c for c in df_bil.columns if 'Valore' in c or 'Importo' in c]

        if poss_cat and poss_val:
            c_cat, c_val = poss_cat[0], poss_val[0]
            def g_v(l): return df_bil[df_bil[c_cat].str.contains(l, na=False, case=False)][c_val].sum()

            liq_val = round(g_v('Attività Correnti') / g_v('Passività Correnti'), 2) if g_v('Passività Correnti') > 0 else 0.0
            solv_val = round(g_v('Patrimonio Netto') / g_v('Passività'), 2) if g_v('Passività') > 0 else 0.0
            stato_rischio = "BASSO" if liq_val > 1.2 else "CRITICO"
            color_border = "#10b981" if liq_val > 1.2 else "#ef4444"
            st.success("✅ Analisi completata")
        else:
            st.error("⚠️ Colonne 'Categoria' o 'Valore' non trovate.")
    except Exception as e:
        st.error(f"Errore: {e}")

# --- CARD RISULTATI ---
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="metric-card" style="border-top: 5px solid {color_border}"><strong>LIQUIDITÀ</strong><h2>{liq_val}</h2></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card" style="border-top: 5px solid #3b82f6;"><strong>SOLVIBILITÀ</strong><h2>{solv_val}</h2></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card" style="border-top: 5px solid {color_border}"><strong>RISCHIO</strong><h2>{stato_rischio}</h2></div>', unsafe_allow_html=True)
