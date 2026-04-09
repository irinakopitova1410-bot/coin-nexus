
import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAZIONE E BLOCCO INTERFACCIA
st.set_page_config(page_title="Coin-Nexus Elite", layout="wide", initial_sidebar_state="collapsed")

# CSS Avanzato per nascondere header, menu e pulsanti di share
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            .stDeployButton {display:none;}
            #stDecoration {display:none;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# 2. STILE DARK ELITE
st.markdown("""
    <style>
    .main { background-color: #0f172a; }
    [data-testid="stMetric"] { background-color: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155; }
    .analysis-box { background-color: #1e293b; border-left: 5px solid #ef4444; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("COIN-NEXUS ELITE")
st.caption("Sistema Gestionale Riservato | Accesso Operatore")

# --- IL TUO DATABASE (Qui modifichi solo tu i dati) ---
data = {
    'ID_Operazione': ['REQ-9901', 'PAY-4402', 'STK-1105', 'REQ-9905', 'PAY-4409', 'PRAT-001'],
    'Sistema': ['SAP', 'Docfinance', 'SO99+', 'SAP', 'Docfinance', 'Telemaco'],
    'Descrizione': ['Acquisto Materie Prime', 'Saldi Fornitore X', 'Sottoscorta Acciaio', 'Ordine Cliente Y', 'Riba in Scadenza', 'Visura Camerale'],
    'Valore_Euro': [15000, 4500, 0, 12000, 8900, 50],
    'Stato': ['In Approvazione', 'In Attesa', 'CRITICO', 'Spedito', 'Da Pagare', 'Inviata']
}
df = pd.DataFrame(data)

# --- MOTORE DI RICERCA ---
search = st.text_input("🔍 Inserisci termine di ricerca (Sistema, ID o Stato)...", "")

if search:
    mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
    df = df[mask]

# --- ANALISI CRITICITÀ ---
if "CRITICO" in search.upper() or (not df.empty and any(df['Stato'] == 'CRITICO')):
    st.error("⚠️ Rilevate anomalie bloccanti. Seguire le procedure di rettifica bilancio.")

# --- DASHBOARD ---
if not df.empty:
    col1, col2 = st.columns(2)
    with col1:
        fig_pie = px.pie(df, names='Sistema', title='Carico Sistemi', hole=0.4)
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_pie, use_container_width=True)
    with col2:
        fig_bar = px.bar(df, x='ID_Operazione', y='Valore_Euro', color='Stato', title='Impatto Economico')
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")
cols = st.columns(3)
for i, row in df.iterrows():
    with cols[i % 3]:
        color = "#ef4444" if row['Stato'] == "CRITICO" else "#38bdf8"
        st.markdown(f"""
            <div style="background:#1e293b; padding:20px; border-radius:15px; border-left: 5px solid {color}; border: 1px solid #334155; margin-bottom:10px;">
                <small style='color:#94a3b8'>{row['Sistema']}</small>
                <div style="font-weight:bold; font-size:18px; color:white;">{row['ID_Operazione']}</div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:10px">
                    <span style="font-weight:bold; color:white">€ {row['Valore_Euro']:,}</span>
                    <span style="background:{color}; padding:2px 8px; border-radius:5px; font-size:10px; color:white">{row['Stato']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
