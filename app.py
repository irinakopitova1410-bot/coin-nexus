import streamlit as st
import pandas as pd
import plotly.express as px

# Configurazione Pagina
st.set_page_config(page_title="Coin-Nexus Elite | Analisi", layout="wide")

# Stile Dark
st.markdown("""
    <style>
    .main { background-color: #0f172a; }
    [data-testid="stMetric"] { background-color: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155; }
    .analysis-box { background-color: #1e293b; border-left: 5px solid #ef4444; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("COIN-NEXUS ELITE")
st.caption("Dashboard Operativa con Intelligenza di Bilancio")

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

# --- LOGICA DI ANALISI BILANCIO (Attivata da "CRITICO") ---
if "CRITICO" in search.upper() or (not df.empty and any(df['Stato'] == 'CRITICO')):
    st.markdown("### 🧠 ANALISI STRATEGICA E AZIONI CORRETTIVE")
    critici = df[df['Stato'] == 'CRITICO']
    
    with st.container():
        st.markdown("<div class='analysis-box'>", unsafe_allow_html=True)
        st.error(f"ATTENZIONE: Rilevate {len(critici)} anomalie bloccanti.")
        
        # Analisi Dinamica
        for _, row in critici.iterrows():
            if row['Sistema'] == 'SO99+':
                st.write(f"**Problema su {row['ID_Operazione']}:** Rilevato blocco produzione per sottoscorta.")
                st.write("👉 **COSA SISTEMARE:** Verificare ordine fornitore su SAP e allineare il lead time in SO99+. Rischio penale ritardo consegna: **Elevato**.")
            elif row['Sistema'] == 'Docfinance':
                st.write(f"**Problema su {row['ID_Operazione']}:** Squilibrio Cash Flow.")
                st.write("👉 **COSA SISTEMARE:** Sollecitare incasso fatture scadute per coprire il debito di € {row['Valore_Euro']}.")
        
        st.markdown("</div>", unsafe_allow_html=True)

# --- SEZIONE GRAFICI ---
if not df.empty:
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    col_kpi1.metric("Valore Gestito", f"€ {df['Valore_Euro'].sum():,}")
    col_kpi2.metric("N. Operazioni", len(df))
    col_kpi3.metric("Rischio Bilancio", "ALTO" if any(df['Stato'] == 'CRITICO') else "BASSO")

    col_chart1, col_chart2 = st.columns(2)
    fig_pie = px.pie(df, names='Sistema', title='Carico Sistemi', hole=0.4)
    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
    col_chart1.plotly_chart(fig_pie, use_container_width=True)

    fig_bar = px.bar(df, x='ID_Operazione', y='Valore_Euro', color='Stato', title='Impatto Economico')
    fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
    col_chart2.plotly_chart(fig_bar, use_container_width=True)

# --- SEZIONE CARD ---
st.markdown("---")
cols = st.columns(3)
for i, row in df.iterrows():
    with cols[i % 3]:
        color = "#ef4444" if row['Stato'] == "CRITICO" else "#38bdf8"
        st.markdown(f"""
            <div style="background:#1e293b; padding:20px; border-radius:15px; border-left: 5px solid {color}; margin-bottom:15px; border: 1px solid #334155;">
                <h4 style="margin:0; color:#38bdf8; font-size:16px;">{row['Sistema']}</h4>
                <div style="font-weight:bold; font-size:18px; color:white; margin:5px 0;">{row['ID_Operazione']}</div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:10px">
                    <span style="font-weight:bold; font-size:18px; color:white">€ {row['Valore_Euro']:,}</span>
                    <span style="background:{color}; padding:2px 8px; border-radius:5px; font-size:10px; font-weight:bold; color:white">{row['Stato']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
