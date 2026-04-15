import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import json

# --- CONFIGURAZIONE DASHBOARD ---
st.set_page_config(page_title="Coin-Nexus | Banking Audit", layout="wide")

# Funzione di calcolo Rating e Bancabilità
def analizza_rating(r, e, d):
    try:
        dscr = e / (d/5 if d > 0 else 1) # Ammortamento teorico a 5 anni
        score = "AAA" if dscr > 2.5 else "BBB" if dscr > 1.2 else "CCC"
        cap_credito = e * 3 if dscr > 1.2 else 0
        return {"score": score, "dscr": dscr, "potenziale": cap_credito}
    except: return None

st.title("🏛️ Coin-Nexus | Business Intelligence")
st.write("Target: Integrazione ERP & Pre-Audit Bancario")

# --- CREAZIONE DEI TAB (Qui apparirà il modulo ERP) ---
tab1, tab2 = st.tabs(["📊 Terminale Analisi", "🔌 ERP Gateway (JSON)"])

with tab1:
    st.subheader("Analisi Manuale")
    c1, c2 = st.columns([1, 2])
    with c1:
        nome = st.text_input("Azienda", "S.p.A. Cliente")
        rev = st.number_input("Ricavi", value=1000000)
        ebit = st.number_input("EBITDA", value=200000)
        deb = st.number_input("Debito", value=300000)
        calcola = st.button("ESEGUI AUDIT")
    
    with c2:
        if calcola:
            res = analizza_rating(rev, ebit, deb)
            st.metric("Rating Sostenibilità", res['score'])
            st.metric("Capacità Nuovi Finanziamenti", f"€ {res['potenziale']:,.0f}")
            fig = go.Figure(go.Indicator(mode="gauge+number", value=res['dscr'], title={'text': "DSCR Index"}))
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("🔌 Connessione ERP Diretta")
    st.info("Copia qui il tracciato record del tuo gestionale (Doc Finance / SAP / Odoo)")
    
    esempio_json = {
        "azienda": "Azienda Esempio",
        "revenue": 5000000,
        "ebitda": 850000,
        "debt": 1200000
    }
    
    input_testo = st.text_area("Payload JSON", value=json.dumps(esempio_json, indent=2), height=200)
    
    if st.button("Sincronizza Dati"):
        try:
            dati = json.loads(input_testo)
            risultato = analizza_rating(dati['revenue'], dati['ebitda'], dati['debt'])
            st.success(f"Analisi completata per {dati['azienda']}")
            st.json(risultato)
        except:
            st.error("Errore: il formato dei dati non è compatibile con l'API di Coin-Nexus.")
