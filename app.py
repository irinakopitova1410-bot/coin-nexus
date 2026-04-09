import streamlit as st
import pandas as pd
import plotly.express as px

# Setup ultra-base per testare il funzionamento
st.set_page_config(page_title="COIN-NEXUS TEST", layout="wide")

st.title("⚡ COIN-NEXUS TITANIUM IS ONLINE")

# Controllo se le librerie sono caricate
st.sidebar.success("Sistema Operativo Attivo")

# Dati di test immediati (senza bisogno di upload)
data = {
    'Voce': ['Cassa', 'Crediti', 'Debiti', 'Patrimonio'],
    'Valore': [500000, 300000, 200000, 600000]
}
df = pd.DataFrame(data)

col1, col2 = st.columns(2)

with col1:
    st.metric("Liquidità Totale", "€ 500.000", "+5%")
    st.write("Se vedi questo, l'app sta funzionando correttamente.")

with col2:
    fig = px.pie(df, names='Voce', values='Valore', hole=0.5, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

st.info("Trascina qui il tuo file Excel nella sidebar per l'analisi reale.")
