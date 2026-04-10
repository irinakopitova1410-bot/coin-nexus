import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF

# CONFIGURAZIONE BASE
st.set_page_config(page_title="COIN-NEXUS", layout="wide")

st.title("💠 COIN-NEXUS PLATINUM")

# Test di caricamento
uploaded_file = st.sidebar.file_uploader("Carica Excel o CSV", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        st.success("File caricato correttamente!")
        st.write(df.head())
        
        # Metriche veloci
        importo_col = [c for c in df.columns if any(x in c.lower() for x in ['saldo', 'importo', 'valore'])][0]
        totale = df[importo_col].sum()
        st.metric("Capitale Totale", f"€ {totale:,.2f}")
        
    except Exception as e:
        st.error(f"Errore: {e}")
else:
    st.info("Carica un file nella barra laterale per iniziare.")
