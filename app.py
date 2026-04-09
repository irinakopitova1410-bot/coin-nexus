import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. CONFIGURAZIONE E BLOCCO INTERFACCIA
st.set_page_config(page_title="Coin-Nexus Elite", layout="wide", initial_sidebar_state="collapsed")

# Nascondiamo i menu di Streamlit per Andrea (blindiamo l'app)
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

# 2. DATABASE INTERNO (Sorgente dati dai 4 sistemi)
data = {
    'ID_Operazione': ['REQ-9901', 'PAY-4402', 'STK-1105', 'REQ-9905', 'PAY-4409', 'PRAT-001'],
    'Sistema': ['SAP', 'Docfinance', 'SO99+', 'SAP', 'Docfinance', 'Telemaco'],
    'Descrizione': ['Acquisto Materie Prime', 'Saldi Fornitore X', 'Sottoscorta Acciaio', 'Ordine Cliente Y', 'Riba in Scadenza', 'Visura Camerale'],
    'Valore_Euro': [15000, 4500, 0, 12000, 8900, 50],
    'Stato': ['In Approvazione', 'In Attesa', 'CRITICO', 'Spedito', 'Da Pagare', 'Inviata']
}
df = pd.DataFrame(data)

# 3. SIDEBAR PER INPUT DI BILANCIO
st.sidebar.header("📊 Parametri Finanziari")
cassa_reale = st.sidebar.number_input("Liquidità Attuale (€)", value=35000)
budget_alert = st.sidebar.slider("Soglia Allerta Rischio (%)", 0, 100, 70)

# --- INIZIO LAYOUT ---
st.title("COIN-NEXUS ELITE")
st.caption("Centrale Operativa Integrata & Simulatore di Rischio Bilancio")

# 4. SEZIONE BILANCIO & RISCHIO (In alto per impatto immediato)
st.subheader("🛡️ Rating di Solidità Aziendale")
totale_impegni = df['Valore_Euro'].sum()
indice_solidita = (cassa_reale / totale_impegni * 100) if totale_impegni > 0 else 100

col_top1, col_top2 = st.columns([1, 2])

with col_top1:
    st.metric("Esposizione Totale (SAP+DF)", f"€ {totale_impegni:,}")
    rating = "SICURO" if indice_solidita > 120 else "⚠️ ATTENZIONE" if indice_solidita > 80 else "🚨 RISCHIO ALTO"
    st.metric("Rating Attuale", rating)

with col_top2:
    # Tachimetro del Rischio
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = indice_solidita,
        title = {'text': "Indice Copertura Cash Flow (%)", 'font': {'size': 18}},
        gauge = {
            'axis': {'range': [0, 200]},
            'bar': {'color': "#38bdf8"},
            'steps' : [
                {'range': [0, 80], 'color': "#ef4444"},
                {'range': [80, 120], 'color': "#f59e0b"},
                {'range': [120, 200], 'color': "#10b981"}]
        }
    ))
    fig_gauge.update_layout(height=250, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
    st.plotly_chart(fig_gauge, use_container_width=True)

st.markdown("---")

# 5. MOTORE DI RICERCA E OPERATIVITÀ
st.subheader("🔍 Monitoraggio Operativo Sistemi")
search = st.text_input("Cerca per Sistema, ID o Stato (es. 'SAP' o 'CRITICO')", "")

if search:
    mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
    df_filtered = df[mask]
else:
    df_filtered = df

# Griglia delle card operative
if df_filtered.empty:
    st.warning("Nessun dato corrispondente alla ricerca.")
else:
    cols = st.columns(3)
    for i, row in df_filtered.iterrows():
        with cols[i % 3]:
            color = "#ef4444" if row['Stato'] == "CRITICO" else "#38bdf8"
            st.markdown(f"""
                <div style="background:#1e293b; padding:15px; border-radius:10px; border-left: 5px solid {color}; border: 1px solid #334155; margin-bottom:10px;">
                    <small style='color:#94a3b8'>{row['Sistema']}</small>
                    <div style="font-weight:bold; color:white;">{row['ID_Operazione']}</div>
                    <div style="font-size:12px; color:#94a3b8; margin: 5px 0;">{row['Descrizione']}</div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-top:10px">
                        <span style="font-weight:bold; color:white">€ {row['Valore_Euro']:,}</span>
                        <span style="background:{color}; padding:2px 8px; border-radius:5px; font-size:10px; color:white">{row['Stato']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
