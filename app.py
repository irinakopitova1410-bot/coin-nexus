import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAZIONE
st.set_page_config(page_title="Coin-Nexus Elite", layout="wide")

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
df = None 

if uploaded_file:
    try:
        # Gestione robusta della lettura file
        if uploaded_file.name.endswith('.csv'):
            try:
                df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='utf-8')
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='ISO-8859-1')
        else:
            df = pd.read_excel(uploaded_file)
        
        # Pulizia nomi colonne
        df.columns = df.columns.str.strip()

        # Identificazione colonne Categoria e Valore
        col_cat = [c for c in df.columns if 'Categoria' in c or 'Voce' in c]
        col_val = [c for c in df.columns if 'Valore' in c or 'Importo' in c]

        if col_cat and col_val:
            c_name, v_name = col_cat[0], col_val[0]
            
            # Calcolo indici con gestione errori
            def get_sum(label):
                return df[df[c_name].str.contains(label, na=False, case=False)][v_name].sum()

            attivo_c = get_sum('Attività Correnti')
            passivo_c = get_sum('Passività Correnti')
            patrimonio = get_sum('Patrimonio Netto')
            passivo_t = get_sum('Passività')

            liq_val = round(attivo_c / passivo_c, 2) if passivo_c > 0 else 0.0
            solv_val = round(patrimonio / passivo_t, 2) if passivo_t > 0 else 0.0
            
            stato_rischio = "BASSO" if liq_val > 1.2 else "CRITICO"
            color_border = "#10b981" if liq_val > 1.2 else "#ef4444"
            st.success("✅ Analisi completata!")
        else:
            st.error("⚠️ Il file deve contenere le colonne 'Categoria' e 'Valore'.")
            df = None

    except Exception as e:
        st.error(f"Errore durante l'elaborazione: {e}")
        df = None

# --- VISUALIZZAZIONE CARD ---
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="metric-card" style="border-top: 5px solid {color_border}"><strong>LIQUIDITÀ</strong><h2>{liq_val}</h2></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card" style="border-top: 5px solid #3b82f6;"><strong>SOLVIBILITÀ</strong><h2>{solv_val}</h2></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card" style="border-top: 5px solid {color_border}"><strong>RISCHIO</strong><h2>{stato_rischio}</h2></div>', unsafe_allow_html=True)

# --- GRAFICO ---
if df is not None:
    st.markdown("### 📈 Ripartizione Voci di Bilancio")
    fig = px.bar(df, x=df.columns[0], y=df.columns[1], template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
