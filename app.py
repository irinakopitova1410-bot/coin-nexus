import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. SETUP PAGINA
st.set_page_config(page_title="Coin-Nexus Elite", layout="wide")

# 2. DATABASE FISSO (Assicuriamoci che ci siano dati di base)
@st.cache_data
def get_data():
    return pd.DataFrame({
        'Sistema': ['SAP', 'Docfinance', 'SO99+', 'SAP', 'Docfinance', 'Telemaco'],
        'ID': ['REQ-9901', 'PAY-4402', 'STK-1105', 'REQ-9905', 'PAY-4409', 'PRAT-01'],
        'Descrizione': ['Acquisto Acciaio', 'Fornitore Luce', 'Sottoscorta', 'Ordine Estero', 'Riba Marzo', 'Visura'],
        'Euro': [15000, 4500, 2000, 12000, 8900, 50],
        'Stato': ['Approvato', 'In Attesa', 'CRITICO', 'Spedito', 'Da Pagare', 'Inviata']
    })

df = get_data()

# CSS per Testo Bianco
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; }
    * { color: white !important; }
    [data-testid="stMetric"] { background-color: #1e293b !important; border: 1px solid #334155 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. LOGICA CALCOLI
st.title("COIN-NEXUS ELITE")
cassa = st.sidebar.number_input("Inserisci Liquidità (€)", value=35000)
totale_debiti = df['Euro'].sum()
# Calcolo della percentuale per il grafico (evita divisione per zero)
percentuale = (cassa / totale_debiti * 100) if totale_debiti > 0 else 0

# 4. IL GRAFICO (Garantiamo che riceva i dati)
col1, col2 = st.columns([1, 1])

with col1:
    st.metric("Liquidità Attuale", f"€ {cassa:,}")
    st.metric("Debiti Totali", f"€ {totale_debiti:,}")

with col2:
    # Creazione del grafico a tachimetro
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = percentuale,
        title = {'text': "Indice di Copertura", 'font': {'color': "white"}},
        number = {'suffix': "%", 'font': {'color': "white"}},
        gauge = {
            'axis': {'range': [0, 200], 'tickcolor': "white"},
            'bar': {'color': "white"},
            'steps': [
                {'range': [0, 80], 'color': "#ff4b4b"},
                {'range': [80, 120], 'color': "#ffa500"},
                {'range': [120, 200], 'color': "#00cc96"}
            ],
        }
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# 5. RICERCA E TABELLA DATI
search = st.text_input("🔍 Filtra sistemi (es. scrive 'SAP' o 'Docfinance')")
if search:
    df_filtered = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
else:
    df_filtered = df

st.write("### Dettaglio Operazioni", df_filtered)
