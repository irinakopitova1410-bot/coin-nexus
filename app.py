import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. CONFIGURAZIONE ESTETICA "ELITE"
st.set_page_config(page_title="Coin-Nexus Elite", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Sfondo e Testi Bianchi */
    .stApp { background-color: #0f172a; }
    * { color: white !important; font-family: 'Inter', sans-serif; }
    
    /* Rettangoli Metriche Puliti */
    [data-testid="stMetric"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 15px !important;
        padding: 20px !important;
    }
    
    /* Forza bianco su numeri e etichette */
    [data-testid="stMetricLabel"] div p { color: #94a3b8 !important; font-size: 14px !important; }
    [data-testid="stMetricValue"] div { color: white !important; font-size: 28px !important; }

    /* Input di ricerca stilizzato */
    .stTextInput input {
        background-color: #1e293b !important;
        color: white !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }
    
    /* Linea divisoria sottile */
    hr { border-color: #334155 !important; opacity: 0.3; }
    
    /* Nascondi elementi Streamlit superflui */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. DATASET INTEGRATO
data = {
    'Sistema': ['SAP', 'Docfinance', 'SO99+', 'SAP', 'Docfinance', 'Telemaco'],
    'ID': ['REQ-9901', 'PAY-4402', 'STK-1105', 'REQ-9905', 'PAY-4409', 'PRAT-01'],
    'Descrizione': ['Acquisto Acciaio', 'Fornitore Luce', 'Sottoscorta', 'Ordine Estero', 'Riba Marzo', 'Visura'],
    'Euro': [15000, 4500, 2000, 12000, 8900, 50],
    'Stato': ['Approvato', 'In Attesa', 'CRITICO', 'Spedito', 'Da Pagare', 'Inviata']
}
df = pd.DataFrame(data)

# 3. LAYOUT SUPERIORE (Rating e Liquidità)
st.title("COIN-NEXUS ELITE")
st.caption("Intelligence Finanziaria & Monitoraggio Sistemi")

cassa = st.sidebar.number_input("Liquidità Attuale (€)", value=35000)
totale_debiti = df['Euro'].sum()
percentuale = (cassa / totale_debiti * 100) if totale_debiti > 0 else 100

col_top1, col_top2 = st.columns([1, 1.2])

with col_top1:
    st.markdown("### 💰 Cash Flow")
    st.metric("Liquidità in Cassa", f"€ {cassa:,}")
    st.metric("Esposizione Totale", f"€ {totale_debiti:,}")
    
    if percentuale > 120:
        st.success(f"STATO: SICURO ({int(percentuale)}%)")
    elif percentuale > 80:
        st.warning(f"STATO: ATTENZIONE ({int(percentuale)}%)")
    else:
        st.error(f"STATO: RISCHIO ({int(percentuale)}%)")

with col_top2:
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = percentuale,
        number = {'suffix': "%", 'font': {'color': "white", 'size': 50}},
        gauge = {'axis': {'range': [0, 200], 'tickcolor': "white"}, 'bar': {'color': "white"},
                 'steps' : [{'range': [0, 80], 'color': "#ef4444"}, {'range': [80, 120], 'color': "#f59e0b"}, {'range': [120, 200], 'color': "#10b981"}]}))
    fig.update_layout(height=300, margin=dict(t=30, b=0, l=20
