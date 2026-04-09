import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(page_title="Coin-Nexus Elite", layout="wide", initial_sidebar_state="collapsed")

# 2. STILE CSS
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

# 3. DATABASE COMPLETO (Senza filtri iniziali)
data = {
    'ID_Operazione': ['REQ-9901', 'PAY-4402', 'STK-1105', 'REQ-9905', 'PAY-4409', 'PRAT-001'],
    'Sistema': ['SAP', 'Docfinance', 'SO99+', 'SAP', 'Docfinance', 'Telemaco'],
    'Descrizione': ['Acquisto Materie Prime', 'Saldi Fornitore X', 'Sottoscorta Acciaio', 'Ordine Cliente Y', 'Riba in Scadenza', 'Visura Camerale'],
    'Valore_Euro': [15000, 4500, 0, 12000, 8900, 50],
    'Stato': ['In Approvazione', 'In Attesa', 'CRITICO', 'Spedito', 'Da Pagare', 'Inviata']
}
df = pd.DataFrame(data)

# 4. SIDEBAR
st.sidebar.header("📊 Parametri Finanziari")
cassa_reale = st.sidebar.number_input("Liquidità Attuale (€)", value=35000)

# --- TITOLO ---
st.title("COIN-NEXUS ELITE")
st.caption("Dashboard Finanziaria e Monitoraggio Sistemi")

# 5. CALCOLO BILANCIO
totale_debiti = df['Valore_Euro'].sum()
indice_solidita = (cassa_reale / totale_debiti * 100) if totale_debiti > 0 else 100

col_fin1, col_fin2 = st.columns([1, 1])

with col_fin1:
    st.markdown("### Situazione Liquidità")
    st.metric("Liquidità (Cassa)", f"€ {cassa_reale:,}")
    st.metric("Debiti Totali", f"€ {totale_debiti:,}")
    
    if indice_solidita > 120:
        st.success(f"✅ SICURO ({int(indice_solidita)}%)")
    elif indice_solidita > 80:
        st.warning(f"⚠️ ATTENZIONE ({int(indice_solidita)}%)")
    else:
        st.error(f"🚨 RISCHIO ALTO ({int(indice_solidita)}%)")

with col_fin2:
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = indice_solidita,
        number = {'suffix': "%", 'font': {'size': 60}},
        gauge = {
            'axis': {'range': [0, 200]},
            'bar': {'color': "white"},
            'steps' : [
                {'range': [0, 80], 'color': "#ff4b4b"},
                {'range': [80, 120], 'color': "#ffa500"},
                {'range': [120, 200], 'color': "#00cc96"}]
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# 6. RICERCA E VISUALIZZAZIONE DATI (Corretta)
st.subheader("🔍 Operatività Sistemi")
search = st.text_input("Filtra per Sistema (SAP, SO99+, Docfinance...) o Stato", "")

# Se la ricerca è vuota, mostra tutto. Se c'è scritto qualcosa, filtra.
if search:
    df_filtered = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
else:
    df_filtered = df

if not df_filtered.empty:
    cols = st.columns(3)
    # Reset dell'indice per evitare errori di posizionamento nelle colonne
    df_filtered = df_filtered.reset_index(drop=True)
    for i, row in df_filtered.iterrows():
        with cols[i % 3]:
            color = "#ef4444" if row['Stato'] == "CRITICO" else "#38bdf8"
            st.markdown(f"""
                <div style="background:#1e293b; padding:15px; border-radius:10px; border-left: 5px solid {color}; border: 1px solid #334155; margin-bottom:10px; min-height:120px;">
                    <small
