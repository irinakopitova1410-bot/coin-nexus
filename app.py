import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. SETUP E FORZATURA CSS BIANCO ASSOLUTO
st.set_page_config(page_title="Coin-Nexus Elite", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Sfondo scuro per tutta l'app */
    .main { background-color: #0f172a !important; }
    
    /* FORZATURA TOTALE TESTI METRICHE */
    /* Questo colpisce l'etichetta (es. Liquidità in Cassa) */
    [data-testid="stMetricLabel"] {
        -webkit-text-fill-color: #ffffff !important;
        color: #ffffff !important;
        font-weight: bold !important;
        opacity: 1 !important;
    }
    
    /* Questo colpisce il numero (es. € 35,000) */
    [data-testid="stMetricValue"] {
        -webkit-text-fill-color: #ffffff !important;
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    /* Stile del rettangolo blu/scuro */
    [data-testid="stMetric"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        padding: 20px !important;
    }

    /* Colore dei titoli generali */
    h1, h2, h3, h4, p { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATI E LOGICA (Il resto rimane uguale)
data = {
    'ID_Operazione': ['REQ-9901', 'PAY-4402', 'STK-1105', 'REQ-9905', 'PAY-4409', 'PRAT-001'],
    'Sistema': ['SAP', 'Docfinance', 'SO99+', 'SAP', 'Docfinance', 'Telemaco'],
    'Descrizione': ['Acquisto Materie Prime', 'Saldi Fornitore X', 'Sottoscorta Acciaio', 'Ordine Cliente Y', 'Riba in Scadenza', 'Visura Camerale'],
    'Valore_Euro': [15000, 4500, 0, 12000, 8900, 50],
    'Stato': ['In Approvazione', 'In Attesa', 'CRITICO', 'Spedito', 'Da Pagare', 'Inviata']
}
df = pd.DataFrame(data)
cassa_reale = st.sidebar.number_input("Liquidità Attuale (€)", value=35000)

# --- VISUALIZZAZIONE ---
st.title("COIN-NEXUS ELITE")
st.markdown("---")

col_t1, col_t2 = st.columns([1, 1])

with col_t1:
    st.subheader("Stato Cassa")
    st.metric(label="Liquidità in Cassa", value=f"€ {cassa_reale:,}")
    # Nota: Se il valore è ancora scuro, ora abbiamo forzato il Webkit-Text-Fill
    
    totale_debiti = df['Valore_Euro'].sum()
    st.metric(label="Debiti Totali Sistemi", value=f"€ {totale_debiti:,}")

with col_t2:
    indice_solidita = (cassa_reale / totale_debiti * 100) if totale_debiti > 0 else 100
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = indice_solidita,
        number = {'suffix': "%", 'font': {'color': "white"}},
        gauge = {'axis': {'range': [0, 200], 'tickcolor': "white"}, 'bar': {'color': "white"},
                 'steps' : [{'range': [0, 80], 'color': "#ff4b4b"}, {'range': [80, 120], 'color': "#ffa500"}, {'range': [120, 200], 'color': "#00cc96"}]}))
    fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
    st.plotly_chart(fig, use_container_width=True)

# SEZIONE CARD (Sempre con scritte forzate bianche)
st.markdown("---")
search = st.text_input("Cerca...", placeholder="Filtra i dati...")
# [Resto del codice per le card...]
