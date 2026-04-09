import streamlit as st
import pandas as pd
import plotly.express as px

# 1. SETUP INTERFACCIA
st.set_page_config(page_title="COIN-NEXUS Intelligence", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #e2e8f0; }
    .indicator-card {
        background-color: #161e2d; padding: 20px; border-radius: 12px;
        border-left: 5px solid #3b82f6; margin-bottom: 20px; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ COIN-NEXUS: AUDIT INTELLIGENCE")

# --- CARICAMENTO INTELLIGENTE ---
file = st.file_uploader("Trascina qui il tuo Bilancio (Excel o CSV)", type=['xlsx', 'csv'])

if file:
    try:
        # Rilevamento automatico del formato per evitare l'errore 'utf-8'
        if file.name.lower().endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            # Se è CSV, prova diverse codifiche per sicurezza
            try:
                df = pd.read_csv(file, sep=None, engine='python', encoding='utf-8')
            except:
                file.seek(0)
                df = pd.read_csv(file, sep=None, engine='python', encoding='latin1')
        
        # Pulizia colonne
        df.columns = df.columns.str.strip()
        
        # Identificazione colonne (Voce e Valore)
        cat_cols = [c for c in df.columns if any(x in c.lower() for x in ['cat', 'voce', 'desc', 'conto'])]
        val_cols = [c for c in df.columns if any(x in c.lower() for x in ['valore', 'importo', 'euro', 'saldo', 'dare', 'avere'])]

        if not cat_cols or not val_cols:
            st.error("❌ Non trovo le colonne necessarie. Il file deve avere intestazioni come 'Voce' e 'Valore'.")
            st.info(f"Colonne rilevate nel tuo file: {list(df.columns)}")
        else:
            c_col = cat_cols[0]
            v_col = val_cols[0]

            # Pulizia e conversione numeri
            df[v_col] = pd.to_numeric(df[v_col].astype(str).replace('[€, ]', '', regex=True), errors='coerce').fillna(0)

            # Funzione di ricerca per indici di bilancio
            def somma(keywords):
                pattern = '|'.join(keywords)
                return df[df[c_col].str.contains(pattern, na=False, case=False)][v_col].sum()

            # Calcoli indici solvibilità
            attivo = somma(['attività correnti', 'attivo circolante', 'liquidità', 'crediti', 'rimanenze'])
            passivo = somma(['passività correnti', 'debiti a breve', 'fornitori', 'banche'])
            patrimonio = somma(['patrimonio netto', 'capitale sociale', 'riserve', 'utile'])
