import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ... (Manteniamo lo stile Dark e le configurazioni precedenti) ...

# DATI DI BILANCIO (Esempio di input che potrai collegare ai tuoi file)
st.sidebar.header("📊 Parametri di Bilancio")
fatturato_previsto = st.sidebar.number_input("Fatturato Annuo Previsto (€)", value=500000)
cassa_disponibile = st.sidebar.number_input("Liquidità Totale (Cassa/Banche) (€)", value=80000)

# Calcolo del Rischio basato sui dati dei 4 sistemi
totale_debiti_sap = df[df['Sistema'].isin(['SAP', 'Docfinance'])]['Valore_Euro'].sum()
indice_rischio = (totale_debiti_sap / cassa_disponibile) if cassa_disponibile > 0 else 1

# --- SEZIONE ANALISI BILANCIO ---
st.header("🛡️ Analisi Rischio & Solidità")

col_risk1, col_risk2, col_risk3 = st.columns(3)

# KPI 1: Copertura Debiti
copertura = (cassa_disponibile / totale_debiti_sap * 100) if totale_debiti_sap > 0 else 100
col_risk1.metric("Copertura Debiti", f"{int(copertura)}%", delta=f"{int(copertura-100)}% vs Target")

# KPI 2: Esposizione su Fatturato
esposizione = (totale_debiti_sap / fatturato_previsto * 100)
col_risk2.metric("Incidenza su Fatturato", f"{esposizione:.1f}%")

# KPI 3: Rating Finale
rating = "SICURO" if copertura > 150 else "ATTENZIONE" if copertura > 100 else "RISCHIO ALTO"
col_risk3.metric("Rating Aziendale", rating)

# --- GRAFICO DEL RISCHIO (TACOMETRO) ---
fig_gauge = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = copertura,
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': "Indice di Solidità Finanziaria (Target > 100%)"},
    gauge = {
        'axis': {'range': [0, 200]},
        'bar': {'color': "#38bdf8"},
        'steps' : [
            {'range': [0, 100], 'color': "#ef4444"},
            {'range': [100, 150], 'color': "#f59e0b"},
            {'range': [150, 200], 'color': "#10b981"}],
        'threshold': {
            'line': {'color': "white", 'width': 4},
            'thickness': 0.75,
            'value': 100}
    }
))
fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
st.plotly_chart(fig_gauge, use_container_width=True)
