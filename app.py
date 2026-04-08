import streamlit as st
import pandas as pd

# Configurazione Pagina
st.set_page_config(page_title="Coin-Nexus Elite", layout="wide")

# Stile Dark Custom
st.markdown("""
    <style>
    .main { background-color: #0f172a; }
    [data-testid="stMetric"] { background-color: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155; }
    </style>
    """, unsafe_allow_html=True)

st.title("COIN-NEXUS ELITE")
st.caption("Dashboard Operativa Integrata | SAP - Docfinance - SO99+")

# Database interno
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

# FILTRO CORRETTO (Evita l'AttributeError)
if search:
    # Cerchiamo in tutte le colonne convertendo tutto in stringa in modo sicuro
    mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
    df = df[mask]

# KPI in alto
col1, col2 = st.columns(2)
col1.metric("Valore Totale Gestito", f"€ {df['Valore_Euro'].sum():,}")
col2.metric("Alert Critici", len(df[df['Stato'] == 'CRITICO']))

# Visualizzazione Card
if df.empty:
    st.warning("Nessun dato trovato per questa ricerca.")
else:
    for i, row in df.iterrows():
        color = "#ef4444" if row['Stato'] == "CRITICO" else "#38bdf8"
        st.markdown(f"""
            <div style="background:#1e293b; padding:20px; border-radius:15px; border-left: 5px solid {color}; margin-bottom:15px; border-top: 1px solid #334155; border-right: 1px solid #334155; border-bottom: 1px solid #334155;">
                <h4 style="margin:0; color:#38bdf8;">{row['Sistema']} - {row['ID_Operazione']}</h4>
                <p style="margin:5px 0; color:#94a3b8; font-size:14px;">{row['Descrizione']}</p>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:10px">
                    <span style="font-weight:bold; font-size:20px; color:white">€ {row['Valore_Euro']:,}</span>
                    <span style="background:{color}; padding:5px 12px; border-radius:8px; font-size:12px; font-weight:bold; color:white">{row['Stato']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
