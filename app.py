import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configurazione base
st.set_page_config(page_title="Coin-Nexus Elite", layout="wide")

# CSS Forza Bianco
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; }
    * { color: white !important; }
    [data-testid="stMetric"] { background-color: #1e293b !important; border: 1px solid #334155 !important; border-radius: 10px; padding: 15px; }
    .stTextInput input { background-color: #1e293b !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# Database semplice per evitare errori
df = pd.DataFrame({
    'Sistema': ['SAP', 'Docfinance', 'SO99+', 'SAP', 'Docfinance'],
    'ID': ['REQ-9901', 'PAY-4402', 'STK-1105', 'REQ-9905', 'PAY-4409'],
    'Descrizione': ['Acquisto Acciaio', 'Fornitore Luce', 'Sottoscorta', 'Ordine Estero', 'Riba Marzo'],
    'Euro': [15000, 4500, 2000, 12000, 8900],
    'Stato': ['Approvato', 'In Attesa', 'CRITICO', 'Spedito', 'Da Pagare']
})

st.title("COIN-NEXUS ELITE")

# Sezione Cassa e Grafico
cassa = st.sidebar.number_input("Cassa (€)", value=35000)
totale = df['Euro'].sum()
perc = (cassa / totale * 100) if totale > 0 else 100

c1, c2 = st.columns(2)
with c1:
    st.metric("Liquidità Disponibile", f"€ {cassa:,}")
    st.metric("Debiti Totali", f"€ {totale:,}")
with c2:
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=perc,
        number={'suffix': "%", 'font': {'color': "white"}},
        gauge={'axis': {'range': [0, 200]}, 'bar': {'color': "white"}}))
    fig.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Barra di ricerca
search = st.text_input("🔍 Cerca Sistema (es. SAP o Docfinance)")
df
