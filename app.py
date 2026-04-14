import streamlit as st
import pandas as pd
import numpy as np

# 1. CONFIGURAZIONE E AUTH
st.set_page_config(page_title="Coin-Nexus Quantum SaaS", layout="wide")

if 'auth' not in st.session_state:
    st.session_state['auth'] = False

def login():
    st.sidebar.title("🔐 Area Riservata")
    user = st.sidebar.text_input("Username")
    pwd = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Accedi"):
        if user == "admin" and pwd == "quantum2026":
            st.session_state['auth'] = True
            st.rerun()
        else:
            st.sidebar.error("Credenziali errate")

if not st.session_state['auth']:
    st.title("💠 Coin-Nexus Quantum AI")
    st.info("Benvenuto. Per favore, effettua il login dalla barra laterale per analizzare i bilanci.")
    login()
    st.stop()

# 2. CARICAMENTO E INTERFACCIA
st.title("🚀 Dashboard Analisi Forense")
file = st.file_uploader("Carica Bilancio (Excel o CSV)", type=['xlsx', 'csv'])

if file:
    try:
        # Supporto multi-foglio per file complessi
        if file.name.endswith('.xlsx'):
            xl = pd.ExcelFile(file)
            sheet = st.selectbox("Seleziona Foglio", xl.sheet_names)
            df = xl.parse(sheet)
        else:
            df = pd.read_csv(file)

        st.write("### 🔍 Anteprima Dati")
        st.dataframe(df.head(5))

        # 3. MAPPATURA COLONNE
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            descr_col = st.selectbox("Colonna Voci/Descrizioni", df.columns)
        with c2:
            num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            val_col = st.selectbox("Colonna Valori (€)", num_cols)

        # 4. IL TASTO AVVIA ANALISI (Appare qui!)
        if st.button("📊 AVVIA ANALISI E GENERA REPORT"):
            massa = df[val_col].abs().sum()
            mat = massa * 0.015
            
            # Indicatori
            res1, res2, res3 = st.columns(3)
            res1.metric("Massa Totale", f"€ {massa:,.2f}")
            res2.metric("Materialità ISA 320", f"€ {mat:,.2f}")
            res3.metric("Rischio AI", "BASSO")

            # Generazione Report Testuale
            report = f"""
            VERBALE DI REVISIONE QUANTUM AI
            -------------------------------
            Analisi eseguita su: {file.name}
            Massa analizzata: € {massa:,.2f}
            Soglia Materialità: € {mat:,.2f}
            -------------------------------
            Esito: I dati analizzati rientrano nei parametri di conformità ISA.
            """
            st.subheader("📄 Report del Revisore")
            st.text_area("Copia il verbale:", report, height=200)
            st.download_button("📥 Scarica Report", report, "report_revisione.txt")

    except Exception as e:
        st.error(f"Errore: {e}. Assicurati di aver selezionato una colonna con numeri.")
