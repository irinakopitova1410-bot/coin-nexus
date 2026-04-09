import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. SETUP E STILE CSS GLOBALE PER TESTI BIANCHI
st.set_page_config(page_title="Coin-Nexus Elite", layout="wide", initial_sidebar_state="collapsed")

# Forziamo il tema scuro e i testi bianchi ovunque
st.markdown("""
    <style>
    /* Sfondo principale scuro */
    .main { background-color: #0f172a; color: white; }
    
    /* Titoli e Sottotitoli Bianchi */
    h1, h2, h3, h4, h5, h6, p, span, label { color: white !important; font-family: 'Arial', sans-serif; }
    
    /* Input di ricerca con testo bianco e sfondo scuro */
    .stTextInput input { color: white !important; background-color: #1e293b !important; border: 1px solid #334155 !important; }
    
    /* Etichette degli indici (ROE, ROS, Current Ratio) bianche */
    [data-testid="stMetricLabel"] p { color: #cbd5e1 !important; font-size: 14px !important; }
    [data-testid="stMetricValue"] div { color: white !important; font-weight: bold !important; }
    
    /* Widget metriche generali */
    [data-testid="stMetric"] { background-color: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155; }
    
    /* Messaggi di successo/errore puliti */
    .stSuccess, .stError { color: white !important; background-color: #1e293b !important; border: 1px solid #334155 !important; }

    /* Nascondere menu Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. DATABASE OPERATIVO
data = {
    'ID_Operazione': ['REQ-9901', 'PAY-4402', 'STK-1105', 'REQ-9905', 'PAY-4409', 'PRAT-001'],
    'Sistema': ['SAP', 'Docfinance', 'SO99+', 'SAP', 'Docfinance', 'Telemaco'],
    'Descrizione': ['Acquisto Materie Prime', 'Saldi Fornitore X', 'Sottoscorta Acciaio', 'Ordine Cliente Y', 'Riba in Scadenza', 'Visura Camerale'],
    'Valore_Euro': [15000, 4500, 0, 12000, 8900, 50],
    'Stato': ['In Approvazione', 'In Attesa', 'CRITICO', 'Spedito', 'Da Pagare', 'Inviata']
}
df = pd.DataFrame(data)

# 3. DATI PER INDICI CONTABILI (Simulati)
utile_netto = 45000
capitale_proprio = 150000
vendite_totali = 280000
# Input cassa spostato nella sidebar per non disturbare il layout
cassa_reale = st.sidebar.number_input("Liquidità Attuale (€)", value=35000)

# --- INIZIO LAYOUT AZIENDALE ---
st.title("COIN-NEXUS ELITE")
st.caption("Dashboard Finanziaria e Controllo Rischi Integrato")

st.markdown("---")

# SEZIONE 1: ANALISI RISCHIO (Tachimetro)
st.subheader("🛡️ Rating di Solidità Aziendale")
totale_debiti = df['Valore_Euro'].sum()
# Calcolo percentuale copertura
indice_solidita = (cassa_reale / totale_debiti * 100) if totale_debiti > 0 else 100

col_t1, col_t2 = st.columns([1, 1])

with col_t1:
    st.markdown("### Riepilogo Cash Flow")
    st.metric("Liquidità Disponibile (Cassa)", f"€ {cassa_reale:,}")
    st.metric("Esposizione Debitoria (Sistemi)", f"€ {totale_debiti:,}")
    
    # Alert Semaforico basato sulla copertura
    if indice_solidita > 120:
        st.success(f"✅ POSIZIONE SICURA ({int(indice_solidita)}%) - Copertura ottimale.")
    elif indice_solidita > 80:
        st.warning(f"⚠️ ATTENZIONE ({int(indice_solidita)}%) - Monitorare scadenze Docfinance.")
    else:
        st.error(f"🚨 RISCHIO ALTO ({int(indice_solidita)}%) - Recupero crediti urgente.")

with col_t2:
    # Tachimetro con testo e numeri bianchi
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = indice_solidita,
        number = {'suffix': "%", 'font': {'size': 40, 'color': "white"}},
        gauge = {'axis': {'range': [0, 200], 'tickcolor': "white"}, 'bar': {'color': "white"},
                 'steps' : [{'range': [0, 80], 'color': "#ff4b4b"}, {'range': [80, 120], 'color': "#ffa500"}, {'range': [120, 200], 'color': "#00cc96"}]}))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white", 'family': "Arial"})
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# SEZIONE 2: NUOVA SEZIONE INDICI CONTABILI (Testi Bianchi forzati via CSS)
st.subheader("📊 Analisi Performance e Indici di Bilancio")
col_i1, col_i2, col_i3 = st.columns(3)
with col_i1:
    st.metric(label="ROE (Redditività Capitale)", value=f"{(utile_netto/capitale_proprio)*100:.
