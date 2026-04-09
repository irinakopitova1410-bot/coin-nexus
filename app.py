import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(page_title="Coin-Nexus Elite", layout="wide", initial_sidebar_state="collapsed")

# 2. STILE CSS PER NASCONDERE MENU E PULIRE INTERFACCIA
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    .main { background-color: #0f172a; }
    [data-testid="stMetric"] { background-color: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155; }
    </style>
    """, unsafe_allow_html=True)

# 3. DATABASE (I tuoi dati dai 4 sistemi)
data = {
    'ID_Operazione': ['REQ-9901', 'PAY-4402', 'STK-1105', 'REQ-9905', 'PAY-4409', 'PRAT-001'],
    'Sistema': ['SAP', 'Docfinance', 'SO99+', 'SAP', 'Docfinance', 'Telemaco'],
    'Descrizione': ['Acquisto Materie Prime', 'Saldi Fornitore X', 'Sottoscorta Acciaio', 'Ordine Cliente Y', 'Riba in Scadenza', 'Visura Camerale'],
    'Valore_Euro': [15000, 4500, 0, 12000, 8900, 50],
    'Stato': ['In Approvazione', 'In Attesa', 'CRITICO', 'Spedito', 'Da Pagare', 'Inviata']
}
df = pd.DataFrame(data)

# 4. SIDEBAR PER SIMULAZIONE
st.sidebar.header("📊 Parametri Finanziari")
cassa_reale = st.sidebar.number_input("Liquidità Attuale (€)", value=35000)

# --- TITOLO ---
st.title("COIN-NEXUS ELITE")
st.caption("Dashboard Finanziaria e Rating di Rischio")

# 5. CALCOLO BILANCIO E RISCHIO
totale_debiti = df['Valore_Euro'].sum()
indice_solidita = (cassa_reale / totale_debiti * 100) if totale_debiti > 0 else 100

# Griglia Superiore: Metric + Grafico
col_fin1, col_fin2 = st.columns([1, 1])

with col_fin1:
    st.markdown("### Situazione Liquidità")
    st.metric("Liquidità (Cassa)", f"€ {cassa_reale:,}")
    st.metric("Debiti Totali", f"€ {totale_debiti:,}")
    
    if indice_solidita > 1
