import streamlit as st
import pandas as pd
import plotly.express as px

# Configurazione Pagina
st.set_page_config(page_title="Coin-Nexus Elite", layout="wide")

# Stile Dark Custom
st.markdown("""
    <style>
    .main { background-color: #0f172a; }
    stMetric { background-color: #1e293b; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("COIN-NEXUS ELITE")
st.caption("Dashboard Operativa Integrata | SAP - Docfinance - SO99+")

# Creazione dati (Database interno)
data = {
    'ID_Operazione': ['REQ-9901', 'PAY-4402', 'STK-1105', 'REQ-9905', 'PAY-4409', 'PRAT-001'],
    'Sistema': ['SAP', 'Docfinance', 'SO99+', 'SAP', 'Docfinance', 'Telemaco'],
    'Descrizione': ['Acquisto Materie Prime', 'Saldi Fornitore X', 'Sottoscorta Acciaio', 'Ordine Cliente Y', 'Riba in Scadenza', 'Visura Camerale'],
    'Valore_Euro': [15000, 4500, 0, 12000, 8900, 50],
    'Stato': ['In Approvazione', 'In Attesa', 'CRITICO', 'Spedito', 'Da Pagare', 'Inviata']
}
df = pd.DataFrame(data)

# Barra di ricerca laterale
search = st.sidebar.text_input("🔍 Ricerca Rapida Universale", "")

# Filtro dati
if search:
    df = df[df.apply(lambda row: search.lower() in row.astype(str).str.lower().values.sum(), axis=1)]

# KPI in alto
col1, col2 = st.columns(2)
col1.metric("Valore Totale Gestito", f"€ {df['Valore_Euro'].sum():,}")
col2.metric("Alert Critici", len(df[df['Stato'] == 'CRITICO']))

# Visualizzazione Card Moderne
for i, row in df.iterrows():
    with st.container():
        color = "red" if row['Stato'] == "CRITICO" else "lightblue"
        st.markdown(f"""
            <div style="background:#1e293b; padding:20px; border-radius:15px; border-left: 5px solid {color}; margin-bottom:10px">
                <h4 style="margin:0; color:#38bdf8;">{row['Sistema']} - {row['ID_Operazione']}</h4>
                <p style="margin:0; color:#94a3b8;">{row['Descrizione']}</p>
                <div style="display:flex; justify-content:space-between; margin-top:10px">
                    <span style="font-weight:bold; font-size:18px">€ {row['Valore_Euro']:,}</span>
                    <span style="background:{color}; padding:20px 12px; border-radius:10px; font-size:12px; color:white">{row['Stato']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
