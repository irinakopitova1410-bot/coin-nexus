
import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAZIONE E BLOCCO INTERFACCIA
st.set_page_config(page_title="Coin-Nexus Elite", layout="wide", initial_sidebar_state="collapsed")
# --- SEZIONE INDICATORI PERFORMANCE (KPI) ---
st.write("### Indicatori Performance Aziendale")

# Creiamo 4 colonne per gli indicatori principali
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(f'''
        <div class="metric-card" style="border-left: 5px solid #3b82f6;">
            <p style="color: #94a3b8; font-size: 0.8rem; margin: 0;">TOTALE ACQUISTI</p>
            <h2 style="margin: 0; color: white;">€ 27.000</h2>
            <p style="color: #10b981; font-size: 0.8rem; margin: 0;">↑ 5.2% vs mese prec.</p>
        </div>
    ''', unsafe_allow_html=True)

with kpi2:
    st.markdown(f'''
        <div class="metric-card" style="border-left: 5px solid #fbbf24;">
            <p style="color: #94a3b8; font-size: 0.8rem; margin: 0;">IN APPROVAZIONE</p>
            <h2 style="margin: 0; color: white;">2 REQ</h2>
            <p style="color: #fbbf24; font-size: 0.8rem; margin: 0;">Attesa risposta SAP</p>
        </div>
    ''', unsafe_allow_html=True)

with kpi3:
    st.markdown(f'''
        <div class="metric-card" style="border-left: 5px solid #ef4444;">
            <p style="color: #94a3b8; font-size: 0.8rem; margin: 0;">FLUSSO CASSA (OUT)</p>
            <h2 style="margin: 0; color: white;">€ 13.400</h2>
            <p style="color: #ef4444; font-size: 0.8rem; margin: 0;">Scadenze Docfinance</p>
        </div>
    ''', unsafe_allow_html=True)

with kpi4:
    st.markdown(f'''
        <div class="metric-card" style="border-left: 5px solid #f87171;">
            <p style="color: #94a3b8; font-size: 0.8rem; margin: 0;">ALLERTA STOCK</p>
            <h2 style="margin: 0; color: white;">CRITICO</h2>
            <p style="color: #f87171; font-size: 0.8rem; margin: 0;">Acciaio sottoscorta</p>
        </div>
    ''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True) # Spaziatore
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
# --- RIGA 95: INIZIO SEZIONE ANALISI RISCHI ---
st.markdown("---")
st.subheader("🛡️ Analisi Solvibilità e Indicatori di Rischio")

# Layout a 3 colonne per gli indici finanziari
r_col1, r_col2, r_col3 = st.columns(3)

with r_col1:
    # Indice di Liquidità (Current Ratio)
    st.markdown('''
        <div style="background-color: #334155; padding: 20px; border-radius: 10px; border-left: 5px solid #10b981; color: white;">
            <small style="color: #94a3b8; text-transform: uppercase;">Liquidità Corrente</small>
            <div style="font-size: 28px; font-weight: bold;">1.85</div>
            <div style="color: #10b981; font-size: 13px;">🟢 Solvibilità a breve garantita</div>
        </div>
    ''', unsafe_allow_html=True)

with r_col2:
    # Indice di Solvibilità (Debt to Equity)
    st.markdown('''
        <div style="background-color: #334155; padding: 20px; border-radius: 10px; border-left: 5px solid #3b82f6; color: white;">
            <small style="color: #94a3b8; text-transform: uppercase;">Solvibilità Totale</small>
            <div style="font-size: 28px; font-weight: bold;">0.42</div>
            <div style="color: #3b82f6; font-size: 13px;">🔵 Struttura finanziaria solida</div>
        </div>
    ''', unsafe_allow_html=True)

with r_col3:
    # Allerta Rischio Operativo (Basato su STK-1105)
    st.markdown('''
        <div style="background-color: #451a1a; padding: 20px; border-radius: 10px; border-left: 5px solid #ef4444; color: white;">
            <small style="color: #f87171; text-transform: uppercase;">Rischio Operativo</small>
            <div style="font-size: 28px; font-weight: bold;">ALTO</div>
            <div style="color: #f87171; font-size: 13px;">🔴 Sottoscorta critico: Acciaio</div>
        </div>
    ''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
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
