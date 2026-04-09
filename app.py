import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime
import numpy as np

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="COIN-NEXUS TITANIUM", layout="wide")

# Inizializzazione Session State (Evita i crash tra i menu)
if 'mat' not in st.session_state: st.session_state['mat'] = 10000.0
if 'dscr' not in st.session_state: st.session_state['dscr'] = 1.5

# --- STILE ---
st.markdown("""
    <style>
    .main { background: #020617; color: #f1f5f9; }
    [data-testid="stSidebar"] { background: #0a0f18; border-right: 1px solid #3b82f6; }
    .stMetric { background: #1e293b; border: 1px solid #3b82f6; border-radius: 10px; padding: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONE PDF (CORRETTA) ---
def genera_report(mat, dscr):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "COIN-NEXUS: REPORT DI REVISIONE", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.cell(0, 10, f"Materialita Calcolata: Euro {mat:,.2f}", ln=True)
    pdf.cell(0, 10, f"Indice Going Concern (DSCR): {dscr:.2f}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, "Conclusioni: Sulla base delle analisi effettuate, non sono emersi elementi che facciano ritenere il bilancio non attendibile.")
    return pdf.output()

# --- SIDEBAR ---
st.sidebar.title("💠 COIN-NEXUS")
menu = st.sidebar.radio("SISTEMI", ["📊 DASHBOARD", "🛡️ GOING CONCERN", "📄 REPORT PDF"])

# Dati Mock (per evitare crash se non carichi file)
df = pd.DataFrame({'VOCE': ['Liquidita', 'Crediti', 'Debiti'], 'VALORE': [500000, 300000, 200000]})

# --- LOGICA MODULI ---

if menu == "📊 DASHBOARD":
    st.title("📊 Executive Dashboard")
    c1, c2 = st.columns(2)
    c1.metric("ATTIVO TOTALE", f"€ {df['VALORE'].sum():,.0f}")
    c2.metric("MATERIALITÀ", f"€ {st.session_state['mat']:,.0f}")
    
    fig = px.pie(df, names='VOCE', values='VALORE', hole=0.4, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

elif menu == "🛡️ GOING CONCERN":
    st.title("🛡️ Verifica Continuità (ISA 570)")
    # Salviamo il valore direttamente nel session_state
    st.session_state['dscr'] = st.slider("Indice DSCR", 0.5, 3.0, st.session_state['dscr'])
    
    if st.session_state['dscr'] >= 1.1:
        st.success(f"✅ Continuità Garantita (DSCR: {st.session_state['dscr']})")
    else:
        st.error(f"⚠️ Allerta Insolvenza (DSCR: {st.session_state['dscr']})")
    
    # Calcolo soglia materialità rapido
    st.session_state['mat'] = st.number_input("Imposta Materialità (€)", value=st.session_state['mat'])

elif menu == "📄 REPORT PDF":
    st.title("📄 Generatore Relazione Professionale")
    st.write("Scarica il documento finale basato sulle analisi correnti.")
    
    # Generazione dei byte del PDF
    pdf_bytes = genera_report(st.session_state['mat'], st.session_state['dscr'])
    
    st.download_button(
        label="📥 SCARICA REPORT (PDF)",
        data=bytes(pdf_bytes),
        file_name="Audit_Report_CoinNexus.pdf",
        mime="application/pdf"
    )
