import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import io

# --- CONFIGURAZIONE ELITE ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM", layout="wide")

# Se vedi questo, l'app sta girando!
st.sidebar.title("💠 COIN-NEXUS PLATINUM")

uploaded_file = st.sidebar.file_uploader("Carica Dataset Bilancio", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        # Caricamento intelligente
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        
        st.title("🛡️ Audit Intelligence & Forensic")
        
        # Mapping dinamico delle colonne
        cols = df.columns.tolist()
        v_cols = [c for c in cols if any(x in str(c).lower() for x in ['saldo', 'importo', 'valore', 'totale'])]
        c_cols = [c for c in cols if any(x in str(c).lower() for x in ['desc', 'voce', 'conto', 'nominativo'])]
        
        if v_cols and c_cols:
            col_v, col_c = v_cols[0], c_cols[0]
            df[col_v] = pd.to_numeric(df[col_v].astype(str).replace('[€, ]', '', regex=True), errors='coerce').fillna(0)
            
            # DASHBOARD
            totale = df[col_v].sum()
            mat = totale * 0.01
            
            c1, c2 = st.columns(2)
            c1.metric("MASSA ANALIZZATA", f"€ {totale:,.2f}")
            c2.metric("MATERIALITÀ (ISA 320)", f"€ {mat:,.2f}")
            
            # ALERT BIG 4
            pericolo = df[df[col_v] > mat]
            if not pericolo.empty:
                st.error(f"🚨 Rilevate {len(pericolo)} anomalie sopra soglia!")
                st.dataframe(pericolo[[col_c, col_v]])
            
            # GRAFICI
            st.plotly_chart(px.treemap(df.nlargest(20, col_v), path=[col_c], values=col_v, template="plotly_dark"))
            
        else:
            st.warning("⚠️ Formato colonne non riconosciuto. Rinomina le colonne in 'Saldo' e 'Descrizione'.")
            
    except Exception as e:
        st.error(f"Errore tecnico: {e}")
else:
    st.info("👋 Sistema Pronto. Carica un file Excel per iniziare l'Audit.")
