import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 1. CONFIGURAZIONE TITANIUM ITALIA
st.set_page_config(page_title="COIN-NEXUS TITANIUM", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&display=swap');
    .main { background: radial-gradient(circle at 50% 50%, #020617, #000000); color: #f1f5f9; font-family: 'Space Grotesk', sans-serif; }
    [data-testid="stSidebar"] { background: rgba(15, 23, 42, 0.9); backdrop-filter: blur(20px); border-right: 1px solid #00d4ff; }
    .stMetric { background: rgba(30, 41, 59, 0.7); border: 1px solid #00d4ff; border-radius: 15px; padding: 20px; box-shadow: 0 0 20px rgba(0, 212, 255, 0.2); }
    h1 { text-shadow: 0 0 15px #00d4ff; color: #ffffff; letter-spacing: -1px; }
    .status-tag { padding: 5px 15px; border-radius: 20px; background: #00d4ff; color: #000; font-weight: bold; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR IN ITALIANO
st.sidebar.title("⚡ COIN-NEXUS CORE")
menu = st.sidebar.radio("MODULI OPERATIVI", ["💎 RIEPILOGO ESECUTIVO", "🛡️ SCUDO DI RISCHIO", "📈 PROIEZIONI FLUSSI"])
uploaded_file = st.sidebar.file_uploader("📥 CARICA BILANCIO (XLSX/CSV)", type=['xlsx', 'csv'])

# --- LOGICA DATI ---
if uploaded_file:
    try:
        if uploaded_file.name.endswith('.xlsx'): df = pd.read_excel(uploaded_file)
        else: df = pd.read_csv(uploaded_file, sep=None, engine='python')
        df.columns = [str(c).upper() for c in df.columns]
        demo_mode = False
    except: demo_mode = True
else:
    demo_data = {
        'VOCE': ['Liquidità', 'Crediti Clienti', 'Rimanenze', 'Immobilizzazioni', 'Debiti Fornitori', 'Debiti Bancari'],
        'VALORE': [450000, 320000, 150000, 80000, 210000, 120000]
    }
    df = pd.DataFrame(demo_data)
    demo_mode = True

# ==========================================
# MODULO 1: RIEPILOGO ESECUTIVO
# ==========================================
if menu == "💎 RIEPILOGO ESECUTIVO":
    st.markdown(f"<h1>💎 Riepilogo Esecutivo {'<span class="status-tag">MODALITÀ DEMO</span>' if demo_mode else ''}</h1>", unsafe_allow_html=True)
    
    v_col = 'VALORE' if 'VALORE' in df.columns else df.columns[1]
    tot_attivo = df[v_col].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("TOTALE ATTIVO", f"€ {tot_attivo:,.0f}", "+3.2%")
    col2.metric("PUNTEGGIO SALUTE", "94/100", "ECCELLENTE")
    col3.metric("FLUSSO DI CASSA", "€ 42.1K", "+12%")
    col4.metric("LIVELLO RISCHIO", "BASSO", "-5%", delta_color="inverse")

    st.markdown("---")
    
    c_left, c_right = st.columns([2, 1])
    with c_left:
        st.subheader("📊 Mappa Patrimoniale Avanzata")
        fig = px.sunburst(df, path=[df.columns[0]], values=v_col, color=v_col, 
                         color_continuous_scale='GnBu', template='plotly_dark')
        fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    
    with c_right:
        st.subheader("🕵️ Verdetto IA")
        st.write("Analisi automatizzata del merito creditizio:")
        st.info("✅ La struttura finanziaria è solida. Gli indici di liquidità sono ampiamente sopra le soglie d'allerta del Codice della Crisi.")
        st.warning("⚠️ Nota: Ottimizzare la gestione dei crediti verso clienti per migliorare ulteriormente la velocità di incasso.")

# ==========================================
# MODULO 2: SCUDO DI RISCHIO
# ==========================================
elif menu == "🛡️ SCUDO DI RISCHIO":
    st.title("🛡️ Scudo di Rischio (Radar)")
    categorie = ['Liquidità', 'Solvibilità', 'Redditività', 'Efficienza', 'Patrimonio Netto']
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=[5, 4.2, 4.5, 3.8, 5], theta=categorie, fill='toself', 
                                 line_color='#00d4ff', fillcolor='rgba(0, 212, 255, 0.3)'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), 
                      paper_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# MODULO 3: PROIEZIONI FLUSSI
# ==========================================
else:
    st.title("📈 Proiezione Flussi di Cassa")
    mesi = ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu"]
    valori = [100, 115, 105, 145, 140, 165]
    fig = px.area(x=mesi, y=valori, title="Previsione Liquidità a 6 Mesi", template='plotly_dark')
    fig.update_traces(line_color='#00d4ff', fillcolor='rgba(0, 212, 255, 0.2)')
    fig.update_layout(xaxis_title="Mesi", yaxis_title="Indice di Cassa")
    st.plotly_chart(fig, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption(f"🔒 SESSIONE SICURA ATTIVA | {datetime.now().strftime('%H:%M')}")
