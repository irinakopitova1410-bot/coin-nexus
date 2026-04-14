import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Coin-Nexus Quantum AI", layout="wide")
st.title("💠 Coin-Nexus Quantum Financial Analytics")

# --- CARICAMENTO FILE UNIVERSALE ---
uploaded_file = st.file_uploader("Carica Bilancio o Piano Finanziario (Excel/CSV)", type=["xlsx", "xls", "csv"])

if uploaded_file:
    try:
        # Gestione Excel con più fogli
        if uploaded_file.name.endswith(('.xlsx', '.xls')):
            xl = pd.ExcelFile(uploaded_file)
            sheet_name = st.selectbox("Seleziona il foglio da analizzare:", xl.sheet_names)
            df = xl.parse(sheet_name)
        else:
            df = pd.read_csv(uploaded_file)

        st.success(f"File caricato: {uploaded_file.name}")
        
        # --- MAPPATURA INTELLIGENTE DELLE COLONNE ---
        st.info("Configura l'analisi selezionando le colonne corrette:")
        col1, col2 = st.columns(2)
        
        with col1:
            # Colonna descrittiva (es. "Voci di Bilancio")
            desc_col = st.selectbox("Colonna Descrizioni:", df.columns)
        
        with col2:
            # Colonna numerica (es. "Valore", "2030", etc.)
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if not numeric_cols:
                st.error("Nessuna colonna numerica trovata!")
                st.stop()
            val_col = st.selectbox("Colonna Valori (€):", numeric_cols)

        # --- MOTORE DI ANALISI QUANTUM ---
        if st.button("🚀 AVVIA ANALISI FORENSE"):
            # Pulizia dati: rimuoviamo i valori nulli e prendiamo il valore assoluto per la massa
            df_clean = df[[desc_col, val_col]].dropna()
            massa_totale = df_clean[val_col].abs().sum()
            
            # Calcolo Materialità ISA 320 (1.5%)
            materialita = massa_totale * 0.015
            
            # Layout Risultati
            m1, m2, m3 = st.columns(3)
            m1.metric("RICAVI / MASSA TOTALE", f"€ {massa_totale:,.2f}")
            m2.metric("MATERIALITÀ ISA 320", f"€ {materialita:,.2f}")
            m3.metric("RISCHIO REVISIONE", "BASSO" if materialita > 10000 else "MEDIO")
            
            st.write("### 📈 Dettaglio Analisi Forense")
            st.dataframe(df_clean)

    except Exception as e:
        st.error(f"Errore durante l'apertura: {e}")
        st.info("Suggerimento: Assicurati che il file non sia protetto da password.")
