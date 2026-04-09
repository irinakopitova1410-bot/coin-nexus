import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. FORZATURA TEMA E CSS (Il segreto è config + CSS)
st.set_page_config(
    page_title="Coin-Nexus Elite", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Questo CSS colpisce chirurgicamente ogni elemento che potrebbe apparire scuro
st.markdown("""
    <style>
    /* Sfondo totale */
    .stApp { background-color: #0f172a; }
    
    /* Forza il colore bianco su TUTTO il testo dell'app */
    * { color: white !important; font-family: 'Inter', sans-serif; }

    /* Rettangolo delle metriche (Liquidità) */
    [data-testid="stMetric"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* Forza il bianco specifico per le Metriche (Label e Valore) */
    [data-testid="stMetricLabel"] > div > p {
        color: #f8fafc !important; /* Bianco sporco/ghiaccio */
        font-size: 16px !important;
    }
    
    [data-testid="stMetricValue"] > div {
        color: #ffffff !important; /* Bianco puro */
        font-size: 35px !important;
        font-weight: 700 !important;
    }

    /* Rende l'input della ricerca leggibile */
    .stTextInput input {
        background-color: #1e293b !important;
        color: white !important;
        border: 1px solid #334155 !important;
    }

    /* Colore delle linee divisorie */
    hr { border-color: #334155 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATI (Esempio)
data = {
    'ID_Operazione': ['REQ-9901', 'PAY-4402', 'STK-1105', 'REQ-9905', 'PAY-4409'],
    'Sistema': ['SAP', 'Docfinance', 'SO99+', 'SAP', 'Docfinance'],
    'Descrizione': ['Acquisto Materie', 'Saldi Fornitore', 'Sottoscorta', 'Ordine Cliente', 'Riba Scadenza'],
    'Valore_Euro': [15000, 4500, 0, 12000, 8900],
    'Stato': ['Approvato', 'In Attesa', 'CRITICO', 'Spedito', 'Da Pagare']
}
df = pd.DataFrame(data)

# 3. INTERFACCIA
st.title("COIN-NEXUS ELITE")
st.markdown("---")

# Sezione Metriche e Tachimetro
col1, col2 = st.columns([1, 1])

with col1:
    st.metric(label="Liquidità in Cassa", value="€ 35,000")
    st.metric(label="Debiti Totali", value=f"€ {df['Valore_Euro'].sum():,}")

with col2:
    # Tachimetro (Plotly usa il suo colore, forziamo bianco qui)
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = 85,
        number = {'suffix': "%", 'font': {'color': "white"}},
        gauge = {'axis': {'range': [0, 200], 'tickcolor': "white"},
                 'bar': {'color': "white"},
                 'steps' : [
                     {'range': [0, 80], 'color': "#ef4444"},
                     {'range': [80, 120], 'color': "#f59e0b"},
                     {'range': [120, 200], 'color': "#10b981"}]}))
    fig.update_layout(height=250, margin=dict(t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("🔍 Analisi Operativa")
#
