import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. SETUP E STILE
st.set_page_config(page_title="Coin-Nexus Elite", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .main { background-color: #0f172a; }
    [data-testid="stMetric"] { background-color: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #06b6d4; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATASET OPERATIVO
data = {
    'ID_Operazione': ['REQ-9901', 'PAY-4402', 'STK-1105', 'REQ-9905', 'PAY-4409', 'PRAT-001'],
    'Sistema': ['SAP', 'Docfinance', 'SO99+', 'SAP', 'Docfinance', 'Telemaco'],
    'Descrizione': ['Acquisto Materie Prime', 'Saldi Fornitore X', 'Sottoscorta Acciaio', 'Ordine Cliente Y', 'Riba in Scadenza', 'Visura Camerale'],
    'Valore_Euro': [15000, 4500, 0, 12000, 8900, 50],
    'Stato': ['In Approvazione', 'In Attesa', 'CRITICO', 'Spedito', 'Da Pagare', 'Inviata']
}
df = pd.DataFrame(data)

# 3. DATI PER INDICI (Simulati)
utile_netto = 45000
capitale_proprio = 150000
vendite_totali = 280000
cassa_reale = st.sidebar.number_input("Liquidità Attuale (€)", value=35000)

# --- INIZIO LAYOUT ---
st.title("COIN-NEXUS ELITE")

# SEZIONE 1: TACHIMETRO (Rischio Immediato)
totale_debiti = df['Valore_Euro'].sum()
indice_solidita = (cassa_reale / totale_debiti * 100) if totale_debiti > 0 else 100

col_t1, col_t2 = st.columns([1, 1])
with col_t1:
    st.metric("Liquidità in Cassa", f"€ {cassa_reale:,}")
    if indice_solidita > 100: st.success("✅ POSIZIONE SOLIDA")
    else: st.error("🚨 COPERTURA INSUFFICIENTE")

with col_t2:
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = indice_solidita,
        number = {'suffix': "%", 'font': {'size': 40}},
        gauge = {'axis': {'range': [0, 200]}, 'bar': {'color': "white"},
                 'steps' : [{'range': [0, 80], 'color': "#ff4b4b"}, {'range': [80, 120], 'color': "#ffa500"}, {'range': [120, 200], 'color': "#00cc96"}]}))
    fig.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# SEZIONE 2: NUOVA SEZIONE INDICI CONTABILI
st.subheader("📊 Indici di Performance Aziendale")
col_i1, col_i2, col_i3 = st.columns(3)
with col_i1:
    st.metric("ROE (Rendimento Capitale)", f"{(utile_netto/capitale_proprio)*100:.1f}%")
with col_i2:
    st.metric("ROS (Margine Vendite)", f"{(utile_netto/vendite_totali)*100:.1f}%")
with col_i3:
    st.metric("Indice Liquidità", "1.8", delta="Ottimale")

st.markdown("---")

# SEZIONE 3: RICERCA E CARD
search = st.text_input("🔍 Cerca nei sistemi (SAP, Docfinance, Stato...)", "")
df_filtered = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else df

cols = st.columns(3)
for i, row in df_filtered.reset_index().iterrows():
    with cols[i % 3]:
        color = "#ef4444" if row['Stato'] == "CRITICO" else "#38bdf8"
        st.markdown(f"""
            <div style="background:#1e293b; padding:15px; border-radius:10px; border-left: 5px solid {color}; border: 1px solid #f97316; margin-bottom:10px;">
                <small style='color:#94a3b8'>{row['Sistema']}</small><br>
                <b>{row['ID_Operazione']}</b><br>
                <span style="font-size:12px; color:#cbd5e1;">{row['Descrizione']}</span><br>
                <div style="margin-top:10px;"><b>€ {row['Valore_Euro']:,}</b> | <small>{row['Stato']}</small></div>
            </div>
        """, unsafe_allow_html=True)
        .card-monitoraggio {
    background-color: #334155; /* Blu-grigio scuro */
    color: #ffffff;            /* Testo bianco */
    padding: 20px;
    border-radius: 8px;
    border-left: 5px solid #3b82f6; /* Accento blu */
    font-family: sans-serif;
}

.critical {
    color: #f87171; /* Rosso chiaro per visibilità su scuro */
    font-weight: bold;
}
