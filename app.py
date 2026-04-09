import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime
import numpy as np

# CONFIGURAZIONE BASE
st.set_page_config(page_title="COIN-NEXUS CORE", layout="wide")

# Inizializzazione variabili di stato
if 'mat' not in st.session_state: st.session_state['mat'] = 15000.0
if 'dscr' not in st.session_state: st.session_state['dscr'] = 1.4

# SIDEBAR E CARICAMENTO
st.sidebar.title("💠 COIN-NEXUS")
uploaded_file = st.sidebar.file_uploader("CARICA BILANCIO", type=['xlsx', 'csv'])

# Dati di fallback
df = pd.DataFrame({'VOCE': ['Liquidità', 'Crediti', 'Debiti', 'Patrimonio'], 'VALORE': [400000, 300000, 200000, 500000]})
lab_col, val_col = 'VOCE', 'VALORE'

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            df = pd.read_csv(uploaded_file)
        df.columns = [str(c).upper().strip() for c in df.columns]
        val_col = df.select_dtypes(include=[np.number]).columns[0]
        lab_col = df.columns[0]
    except:
        st.sidebar.error("Errore lettura file. Uso dati demo.")

# MENU
menu = st.sidebar.radio("SISTEMI", ["📊 DASHBOARD", "🛡️ GOING CONCERN", "🕵️ FORENSIC", "📄 REPORT"])

if menu == "📊 DASHBOARD":
    st.title("📊 Financial Intelligence")
    st.metric("TOTAL ASSETS", f"€ {df[val_col].sum():,.0f}")
    fig = px.sunburst(df, path=[lab_col], values=val_col, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

elif menu == "🛡️ GOING CONCERN":
    st.title("🛡️ Verifica Continuità (ISA 570)")
    st.session_state['dscr'] = st.slider("Indice DSCR", 0.5, 3.0, float(st.session_state['dscr']))
    
    # Radar Chart - Sintassi ultra-semplificata
    fig = go.Figure(data=go.Scatterpolar(
        r=[5, 4, 3, 5, 4],
        theta=['Liquidità', 'Solvibilità', 'Redditività', 'Efficienza', 'Patrimonio'],
        fill='toself'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

elif menu == "🕵️ FORENSIC":
    st.title("🕵️ Forensic Audit (Benford's Law)")
    st.info("Analisi statistica per l'individuazione di manipolazioni contabili.")
    digits = [int(str(abs(x))[0]) for x in df[val_col] if x != 0]
    if digits:
        actual = np.histogram(digits, bins=range(1, 11))[0] / len(digits)
        expected = [np.log10(1 + 1/d) for d in range(1, 10)]
        fig_b = go.Figure()
        fig_b.add_trace(go.Bar(x=list(range(1,10)), y=actual, name='Reale'))
        fig_b.add_trace(go.Scatter(x=list(range(1,10)), y=expected, name='Benford', line=dict(color='red')))
        fig_b.update_layout(template="plotly_dark")
        st.plotly_chart(fig_b, use_container_width=True)

else:
    st.title("📄 Report PDF")
    if st.button("🛠️ GENERA DOCUMENTO"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "RELAZIONE DI REVISIONE COIN-NEXUS", ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Materialità: Euro {st.session_state['mat']:,.2f}", ln=True)
        pdf.cell(0, 10, f"Indice DSCR: {st.session_state['dscr']:.2f}", ln=True)
        
        pdf_bytes = pdf.output()
        st.download_button(label="📥 SCARICA PDF", data=bytes(pdf_bytes), file_name="Report_Audit.pdf", mime="application/pdf")
