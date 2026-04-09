import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAZIONE GENERALE (Deve essere la prima riga)
st.set_page_config(page_title="Coin-Nexus Elite", layout="wide", initial_sidebar_state="collapsed")

# 2. STILE CSS PERSONALIZZATO
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: white; }
    .metric-card {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 15px;
        transition: 0.3s;
    }
    .metric-card:hover { border-color: #3b82f6; }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stTable { background-color: #1e293b; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("COIN-NEXUS ELITE")
st.caption("Intelligence Finanziaria & Gestione Rischi | Operatore Autorizzato")

# --- SEZIONE 1: KPI OPERATIVI FISSI ---
st.markdown("### 📊 Overview Operativa")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Acquisti Mese", "€ 27.450", "+5.2%")
k2.metric("Richieste SAP", "2 Pendenti", "In approvazione")
k3.metric("Stock Acciaio", "SOTTOSCORTA", "-12%", delta_color="inverse")
k4.metric("Scadenze Docfinance", "€ 13.400", "Settimana prox")

st.markdown("---")

# --- SEZIONE 2: UPLOAD E ANALISI BILANCIO ---
st.header("🛡️ Analisi Solvibilità e Indicatori di Bilancio")
st.info("Trascina qui il file Excel o CSV del bilancio per calcolare gli indici in tempo reale.")

uploaded_file = st.file_uploader("Carica Bilancio", type=["csv", "xlsx"])

# Inizializzazione variabili (Valori di fallback se non c'è file)
liq_val, solv_val, stato_rischio, color_border = 0.0, 0.0, "ATTESA DATI", "#94a3b8"

if uploaded_file:
    try:
        # Lettura Intelligente
        if uploaded_file.name.endswith('.csv'):
            try:
                df_bil = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='utf-8')
            except:
                uploaded_file.seek(0)
                df_bil = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='latin1')
        else:
            df_bil = pd.read_excel(uploaded_file)
        
        # Logica di Analisi Bilancio
        # Cerchiamo colonne che contengono 'Categoria' e 'Valore'
        col_cat = [c for c in df_bil.columns if 'Categoria' in c or 'Voce' in c][0]
        col_val = [c for c in df_bil.columns if 'Valore' in c or 'Importo' in c][0]

        # Calcolo Indici
        def get_sum(label):
            return df_bil[df_bil[col_cat].str.contains(label, na=False, case=False)][col_val].sum()

        attivo_corr = get_sum('Attività Correnti')
        passivo_corr = get_sum('Passività Correnti')
        patrimonio = get_sum('Patrimonio Netto')
        passiv_tot = get_sum('Passività')

        # Calcolo Indice Liquidità (Current Ratio)
        liq_val = round(attivo_corr / passivo_corr, 2) if passivo_corr > 0 else 0.0
        # Calcolo Indice Solvibilità
        solv_val = round(patrimonio / passiv_tot, 2) if passiv_tot > 0 else 0.0
        
        # Alert Dinamici
        if liq_val > 1.2:
            stato_rischio = "BASSO"
            color_border = "#10b981" # Verde
        elif liq_val > 0.8:
            stato_rischio = "MEDIO"
            color_border = "#fbbf24" # Giallo
        else:
            stato_rischio = "CRITICO"
            color_border = "#ef4444" # Rosso

        st.success(f"✅ Analisi completata per {uploaded_file.name}")

    except Exception as e:
        st.error(f"Errore nella struttura del file: Assicurati che ci siano le colonne 'Categoria' e 'Valore'.")

# --- VISUALIZZAZIONE CARD FINANZIARIE ---
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f'''
        <div class="metric-card" style="border-left: 8px solid {color_border};">
            <small style="color: #94a3b8;">LIQUIDITÀ CORRENTE</small>
            <h2 style="margin: 5px 0;">{liq_val}</h2>
            <p style="color: {color_border}; font-size: 0.8rem;">Target: > 1.2</p>
        </div>
    ''', unsafe_allow_html=True)

with c2:
    st.markdown(f'''
        <div class="metric-card" style="border-left: 8px solid #3b82f6;">
            <small style="color: #94a3b8;">SOLVIBILITÀ (D/E)</small>
            <h2 style="margin: 5px 0;">{solv_val}</h2>
            <p style="color: #3b82f6; font-size: 0.8rem;">Solidità Patrimoniale</p>
        </div>
    ''', unsafe_allow_html=True)

with c3:
    st.markdown(f'''
        <div class="metric-card" style="border-left: 8px solid {color_border}; background-color: {'#451a1a' if stato_rischio == 'CRITICO' else '#1e293b'};">
            <small style="color: #94a3b8;">RATING RISCHIO</small>
            <h2 style="margin: 5px 0;">{stato_rischio}</h2>
            <p style="color: {color_border}; font-size: 0.8rem;">Basato su Cash Flow</p>
        </div>
    ''', unsafe_allow_html=True)

# --- SEZIONE 3: GRAFICI E TABELLE ---
if uploaded_file:
    st.markdown("### 📈 Dettaglio Voci di Bilancio")
    fig = px.bar(df_bil, x=col_cat, y=col_val, color=col_cat, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.markdown("### 📋 Registro Operazioni Correnti (Demo)")
    # Tabella finta per riempire lo spazio se non c'è upload
    demo_data = {
        "Data": ["01/04", "05/04", "08/04"],
        "Voce": ["Riba Fornitore Acciaio", "Incasso Cliente X", "Acquisto Utensileria"],
        "Importo": ["- € 8.000", "+ € 15.000", "- € 1.200"],
        "Stato": ["Docfinance", "Banca", "SAP"]
    }
    st.table(demo_data)
