import streamlit as st
import pandas as pd

# Setup essenziale per evitare il crash iniziale
st.set_page_config(page_title="COIN-NEXUS PLATINUM", layout="wide")

st.title("💠 COIN-NEXUS PLATINUM")

# Test rapido di funzionamento
st.sidebar.success("Sistema Operativo")
uploaded_file = st.sidebar.file_uploader("Carica un file per testare l'IA", type=['csv', 'xlsx'])

if uploaded_file:
    st.write("✅ File ricevuto! Analisi in corso...")
    try:
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"Errore tecnico: {e}")
else:
    st.info("In attesa di dati per attivare i motori di Audit.")
