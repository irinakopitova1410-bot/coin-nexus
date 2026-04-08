import streamlit as st
import pandas as pd
import plotly.express as px

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
st.caption("Dashboard Operativa Integrata | SAP - Docfinance - SO99+ - Telemaco")

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

# Filtro
if search:
    mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
    df = df[mask]

# --- SEZIONE GRAFICI ---
if not df.empty:
    col_kpi1, col_kpi2 = st.columns(2)
    col_kpi1.metric("Valore Totale", f"€ {df['Valore_Euro'].sum():,}")
    col_kpi2.metric("Operazioni Totali", len(df))

    st.markdown("---")
    
    col_chart1, col_chart2 = st.columns(2)
    
    # Grafico 1: Distribuzione Sistemi (Torta)
    fig_pie = px.pie(df, names='Sistema', title='Carico per Sistema', hole=0.4,
                     color_discrete_sequence=px.colors.sequential.RdBu)
    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
    col_chart1.plotly_chart(fig_pie, use_container_width=True)

    # Grafico 2: Valori per Operazione (Barre)
    fig_bar = px.bar(df, x='ID_Operazione', y='Valore_Euro', color='Sistema', title='Analisi Valori €',
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
    col_chart2.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("---")

# --- SEZIONE CARD ---
if df.empty:
    st.warning("Nessun dato trovato per questa ricerca.")
else:
    # Mostriamo le card in una griglia di 3 colonne
    cols = st.columns(3)
    for i, row in df.iterrows():
        with cols[i % 3]:
            color = "#ef4444" if row['Stato'] == "CRITICO" else "#38bdf8"
            st.markdown(f"""
                <div style="background:#1e293b; padding:20px; border-radius:15px; border-left: 5px solid {color}; margin-bottom:15px; border: 1px solid #334155;">
                    <h4 style="margin:0; color:#38bdf8; font-size:16px;">{row['Sistema']}</h4>
                    <div style="font-weight:bold; font-size:18px; color:white; margin:5px 0;">{row['ID_Operazione']}</div>
                    <p style="margin:5px 0; color:#94a3b8; font-size:12px; height:30px;">{row['Descrizione']}</p>
                    <hr style="border:0.5px solid #334155">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:bold; font-size:18px; color:white">€ {row['Valore_Euro']:,}</span>
                        <span style="background:{color}; padding:2px 8px; border-radius:5px; font-size:10px; font-weight:bold; color:white">{row['Stato']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
