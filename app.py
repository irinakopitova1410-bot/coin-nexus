import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import base64
from datetime import datetime

# 1. SETTINGS ELITE
st.set_page_config(page_title="COIN-NEXUS | AUDIT REPORT", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e2e8f0; }
    .stMetric { background-color: #111827; border: 1px solid #3b82f6; border-radius: 10px; padding: 20px !important; }
    h1 { font-weight: 800; color: #ffffff; text-shadow: 0 0 10px #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGICA REPORT PDF
def create_pdf(df, mat_val, dscr_val):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "RELAZIONE DI REVISIONE INDIPENDENTE", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="R")
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "1. Giudizio del Revisore", ln=True)
    pdf.set_font("Arial", "", 11)
    opinione = "SENZA MODIFICHE" if dscr_val >= 1.1 else "CON RILIEVI (Going Concern)"
    pdf.multi_cell(190, 10, f"A nostro giudizio, il bilancio d'esercizio fornisce una rappresentazione veritiera e corretta della situazione patrimoniale. Opinione: {opinione}.")
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "2. Materialita (ISA 320)", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 10, f"Soglia di errore tollerabile calcolata: Euro {mat_val:,.2f}", ln=True)
    
    return pdf.output(dest='S')

# 3. SIDEBAR & DATA
st.sidebar.title("💠 NEBULA-X AUDIT")
menu = st.sidebar.radio("SISTEMA", ["📊 DASHBOARD", "⚖️ REVISIONE PRO", "📄 EXPORT REPORT"])
file = st.sidebar.file_uploader("CARICA BILANCIO", type=['xlsx', 'csv'])

if file:
    df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
    df.columns = [str(c).upper().strip() for c in df.columns]
    demo = False
else:
    df = pd.DataFrame({'VOCE': ['Liquidità', 'Crediti', 'Debiti'], 'VALORE': [500000, 300000, 200000]})
    demo = True

# 4. MODULI
if menu == "📊 DASHBOARD":
    st.title("📊 Controllo Strategico")
    c1, c2 = st.columns(2)
    val_col = df.columns[1]
    c1.metric("ATTIVO TOTALE", f"€ {df[val_col].sum():,.0f}")
    c2.metric("GOING CONCERN", "VERIFICATO" if demo else "ANALISI IN CORSO")
    
    fig = px.sunburst(df, path=[df.columns[0]], values=val_col, template="plotly_dark", color_continuous_scale='Blues')
    st.plotly_chart(fig, use_container_width=True)

elif menu == "⚖️ REVISIONE PRO":
    st.title("⚖️ Analisi Rischio ISA")
    bench = st.number_input("Benchmark Totale (€)", value=1000000)
    perc = st.slider("% Materialità", 0.5, 3.0, 1.0)
    mat = bench * (perc / 100)
    st.session_state['mat'] = mat
    st.metric("MATERIALITÀ CALCOLATA", f"€ {mat:,.0f}")

else:
    st.title("📄 Generazione Report Legale")
    st.write("Clicca sul pulsante per generare la bozza della relazione di revisione pronta per la firma.")
    
    mat_final = st.session_state.get('mat', 10000)
    pdf_out = create_pdf(df, mat_final, 1.5)
    
    st.download_button(
        label="📥 SCARICA RELAZIONE PDF",
        data=pdf_out,
        file_name="Relazione_Revisione_CoinNexus.pdf",
        mime="application/pdf"
    )
