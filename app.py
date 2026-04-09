import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF

# --- CONFIGURAZIONE INTERFACCIA ---
st.set_page_config(page_title="Coin-Nexus Platinum", layout="wide")

# --- MOTORE DI MAPPATURA INTELLIGENTE ---
def smart_mapper(df):
    """
    Cerca di identificare le colonne chiave analizzando nomi e contenuti.
    """
    mapping = {}
    columns = df.columns
    
    # Dizionario dei sinonimi per le Big 4
    synonyms = {
        'ricavi': ['fatturato', 'sales', 'revenue', 'ricavi', 'valore della produzione'],
        'liquidita': ['cassa', 'banca', 'cash', 'disponibilità liquide'],
        'debiti': ['passività', 'liabilities', 'debiti', 'payables']
    }
    
    for key, words in synonyms.items():
        for col in columns:
            # Controllo se il nome della colonna contiene una parola chiave
            if any(word in col.lower() for word in words):
                mapping[key] = col
                break
    return mapping

# --- INTERFACCIA UTENTE ---
st.title("💠 Coin-Nexus Platinum: Audit Intelligence")
st.markdown("---")

uploaded_file = st.sidebar.file_uploader("Carica il Bilancio o il Libro Giornale (CSV/XLSX)", type=['csv', 'xlsx'])

if uploaded_file:
    # Caricamento dati
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    # Esecuzione mappatura
    mappa = smart_mapper(df)
    
    st.write("### 🔍 Analisi Mappatura Dati")
    if 'ricavi' in mappa:
        st.success(f"Colonna Ricavi identificata: **{mappa['ricavi']}**")
    else:
        st.warning("Non ho trovato una colonna Ricavi chiara. Selezionala tu:")
        mappa['ricavi'] = st.selectbox("Seleziona colonna Ricavi", df.columns)
