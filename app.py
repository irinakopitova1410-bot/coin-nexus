import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. CONFIGURAZIONE E TEMA
st.set_page_config(page_title="Coin-Nexus Elite", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0f172a; }
    * { color: white !important; }
    [data-testid="stMetric"] { background-color: #1e293b !important; border-radius: 10px; padding: 15px; border: 1px solid #334155; }
    .stTextInput input { background-color: #1e293b !important; color: white !important; border: 1px solid #334155 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATABASE (Assicuriamoci che i dati siano qui)
data = {
    'Sistema': ['SAP', 'Docfinance', 'SO99+', 'SAP', 'Docfinance', 'Telemaco'],
    'ID': ['REQ-9901', 'PAY-4402', 'STK-1105', 'REQ-9905', 'PAY-4409', 'PRAT-01'],
    'Descrizione': ['Acquisto Acciaio', 'Fornitore Luce', 'Sottoscorta', 'Ordine Estero', 'Riba Marzo', 'Visura'],
    'Euro': [15000, 4500, 0, 12000, 8900, 50],
    'Stato': ['Approvato', 'In Attesa', 'CRITICO', 'Spedito', 'Da Pagare', 'Inviata']
}
df = pd.DataFrame(data)

# 3. INTERFACCIA SUPERIORE
st.title("COIN-NEXUS ELITE")
cassa = st.sidebar.number_input("Cassa Reale (€)", value=35000)

col1, col2 = st.columns(2)
with col1:
    st.metric("Liquidità in Cassa", f"€ {cassa:,}")
    debiti = df['Euro'].sum()
    st.metric("Totale Debiti", f"€ {debiti:,}")

with col2:
    perc = (cassa / debiti * 100) if debiti > 0 else 100
