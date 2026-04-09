import streamlit as st
import pandas as pd
import plotly.express as px

# 1. DESIGN & INTERFACCIA ELITE
st.set_page_config(page_title="Coin-Nexus Audit", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #e2e8f0; }
    .stMetric { background-color: #161e2d !important; border: 1px solid #1e293b; padding: 20px; border-radius: 12px; }
    .audit-card { background-color: #161e2d; padding: 20px; border-radius: 12px; border-left: 5px solid #3b82f6; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ COIN-NEXUS: AUDIT INTELLIGENCE")
st.caption("Analisi Solvibilità & Indicatori della Crisi d'Impresa (CCII)")

# --- CARICAMENTO ---
uploaded_file = st.file_uploader("📂 Carica Bilancio (XLSX o CSV)", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        # Lettura automatica
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='latin1')
        
        # Pulizia colonne
        df.columns = [str(c).strip() for c in df.columns]
        
        # Identificazione Colonne (Flessibile)
        c_col = [c for c in df.columns if any(x in c.lower() for x in ['voce', 'desc', 'conto', 'cat'])][0]
        v_col = [c for c in df.columns if any(x in c.lower() for x in ['valore', 'importo', 'saldo', 'euro'])][0]
        
        # Pulizia Valori Numerici
        df[v_col] = pd.to_numeric(df[v_col].astype(str).replace('[€, ]', '', regex=True), errors='coerce').fillna(0)

        # --- LOGICA DEL REVISORE (Somma Masse Patrimoniali) ---
        def get_v(keywords):
            mask = df[c_col].str.contains('|'.join(keywords), na=False, case=False)
            return df[mask][v_col].sum()

        # Calcolo Masse per Indici di Allerta
        liquidita = get_v(['cassa', 'banca', 'disponibilità'])
        crediti = get_v(['clienti', 'crediti v/clienti'])
        magazzino = get_v(['rimanenze', 'magazzino', 'scorte'])
        passivo_breve = get_v(['fornitori', 'banche c/c', 'debiti tributari', 'debiti a breve'])
        patrimonio = get_v(['patrimonio netto', 'capitale sociale', 'riserve', 'utile'])
        debiti_tot = get_v(['passività', 'totale debiti', 'mutui', 'tfr'])

        # --- INDICI CHIAVE ---
        # 1. Liquidità Corrente (Target > 1.2)
        liq_index = round((liquidita + crediti + magazzino) / passivo_breve, 2) if passivo_breve > 0 else 0
        
        # 2. Solvibilità (Patrimonio su Totale Debiti)
        solv_index = round(patrimonio / (patrimonio + debiti_tot), 2) if (patrimonio + debiti_tot) > 0 else 0

        # --- DASHBOARD KPI ---
        k1, k2, k3 = st.columns(3)
        
        status_l = "✅ OK" if liq_index > 1.2 else "⚠️ TENSIONE" if liq_index > 1 else "🚨 ALLERTA"
        k1.metric("Indice Liquidità", liq_index, status_l)
        
        status_s = "✅ SOLIDO" if solv_index > 0.25 else "⚠️ DEBOLE"
        k2.metric("Solvibilità (Grado Autonomia)", f"{solv_index*100:.1f}%", status_s)
        
        k3.metric("Patrimonio Netto", f"€ {patrimonio:,.0f}")

        st.markdown("---")

        # --- ANALISI VISIVA ---
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            st.subheader("🕵️ Verdetto Revisione")
            if liq_index < 1:
                st.error("SQUILIBRIO RILEVATO: Le attività correnti non coprono i debiti a breve termine. Rischio crisi imminente.")
            elif solv_index < 0.15:
                st.warning("STRUTTURA DEBOLE: L'azienda è fortemente indebitata verso terzi. Necessaria ricapitalizzazione.")
            else:
                st.success("EQUILIBRIO: Gli indicatori non mostrano segnali di crisi ai sensi del CCII.")

        with col_right:
            st.subheader("📊 Analisi Asset Correnti")
            asset_df = pd.DataFrame({
                'Voce': ['Liquidità', 'Crediti', 'Magazzino'],
                'Valore': [liquidita, crediti, magazzino]
            })
            fig = px.pie(asset
