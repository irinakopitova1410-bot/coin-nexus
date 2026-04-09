import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. SETUP & STILE ELITE
st.set_page_config(page_title="COIN-NEXUS Intelligence", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #e2e8f0; }
    .stMetric { background-color: #161e2d !important; border: 1px solid #1e293b; padding: 20px; border-radius: 12px; }
    .sidebar .sidebar-content { background-color: #111827; }
    .reportview-container .main .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. MENU LATERALE (NAVIGAZIONE)
st.sidebar.title("🛡️ COIN-NEXUS SYSTEM")
st.sidebar.subheader("Menu Navigazione")
app_mode = st.sidebar.radio("Seleziona il Modulo:", 
    ["🕵️ Audit & Revisore", "🏦 Rating Basilea", "📊 Analisi Centrale Rischi", "📉 Stress Test & What-If"])

# --- CARICAMENTO FILE UNIVERSALE ---
st.sidebar.markdown("---")
file = st.sidebar.file_uploader("📂 Carica Bilancio (XLSX/CSV)", type=['xlsx', 'csv'])

def clean_data(file):
    if file.name.endswith('.xlsx'):
        df = pd.read_excel(file, engine='openpyxl')
    else:
        df = pd.read_csv(file, sep=None, engine='python', encoding='latin1')
    df.columns = [str(c).strip() for c in df.columns]
    return df

# ==========================================
# MODULO 1: AUDIT & REVISORE
# ==========================================
if app_mode == "🕵️ Audit & Revisore":
    st.title("🕵️ Audit Professionale & Revisione")
    if file:
        df = clean_data(file)
        c_col = [c for c in df.columns if any(x in c.lower() for x in ['voce', 'desc', 'conto'])][0]
        v_col = [c for c in df.columns if any(x in c.lower() for x in ['valore', 'importo', 'saldo'])][0]
        df[v_col] = pd.to_numeric(df[v_col].astype(str).replace('[€, ]', '', regex=True), errors='coerce').fillna(0)
        
        # Logica Revisore
        liq = df[df[c_col].str.contains('cassa|banca|liquid', case=False, na=False)][v_col].sum()
        deb = df[df[c_col].str.contains('fornitori|tributari|breve', case=False, na=False)][v_col].sum()
        ratio = round(liq/deb, 2) if deb > 0 else 0
        
        m1, m2 = st.columns(2)
        m1.metric("Cash Ratio", ratio, "Soglia sicura > 0.2")
        m2.metric("Liquidità Immediata", f"€ {liq:,.0f}")
        
        st.plotly_chart(px.bar(df.nlargest(10, v_col), x=v_col, y=c_col, orientation='h', template="plotly_dark"))
    else:
        st.info("Carica un bilancio per iniziare l'audit.")

# ==========================================
# MODULO 2: RATING BASILEA (Dal tuo Colab)
# ==========================================
elif app_mode == "🏦 Rating Basilea":
    st.title("🏦 Simulatore Rating Bancario (Basilea 4)")
    st.write("Valutazione del merito creditizio basata su algoritmi bancari.")
    
    col1, col2 = st.columns(2)
    ebitda = col1.number_input("EBITDA (€)", value=50000)
    pfm = col2.number_input("Posizione Finanziaria Netta (€)", value=150000)
    
    score = round(pfm / ebitda, 2) if ebitda > 0 else 10
    
    if score < 3:
        st.success(f"Rating: EXCELLENT (PFN/EBITDA: {score})")
    elif score < 6:
        st.warning(f"Rating: WATCHLIST (PFN/EBITDA: {score})")
    else:
        st.error(f"Rating: HIGH RISK (PFN/EBITDA: {score})")

# ==========================================
# MODULO 3: CENTRALE RISCHI
# ==========================================
elif app_mode == "📊 Analisi Centrale Rischi":
    st.title("📊 Analisi Centrale Rischi")
    st.write("Monitoraggio segnalazioni e sconfinamenti.")
    
    accordato = st.slider("Fidi Accordati (€)", 10000, 500000, 100000)
    utilizzato = st.slider("Fidi Utilizzati (€)", 10000, 600000, 80000)
    
    tensione = (utilizzato / accordato) * 100
    st.progress(min(tensione/100, 1.0))
    st.metric("Tensione Finanziaria", f"{tensione:.1f}%", delta="-5% rispetto a ieri")

# ==========================================
# MODULO 4: STRESS TEST
# ==========================================
else:
    st.title("📉 Stress Test & What-If")
    st.write("Simulazione impatto calo fatturato sulla cassa.")
    
    calo_fatturato = st.select_slider("Scenario Calo Fatturato:", options=[0, 10, 20, 30, 40, 50])
    
    st.error(f"In caso di calo del {calo_fatturato}%, l'azienda necessita di € {calo_fatturato * 1500:,.0f} di nuova finanza.")
    
    # Grafico Stress
    stress_df = pd.DataFrame({'Scenario': ['Attuale', 'Stress'], 'Cassa': [100, 100 - calo_fatturato]})
    st.plotly_chart(px.area(stress_df, x='Scenario', y='Cassa', title="Erosione della Cassa", template="plotly_dark"))
