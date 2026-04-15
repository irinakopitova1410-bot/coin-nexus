import streamlit as st
import plotly.graph_objects as go
from supabase import create_client, Client
import pandas as pd
from fpdf import FPDF

# --- 1. CONFIGURAZIONE ---
st.set_page_config(page_title="Coin-Nexus Terminal", layout="wide", page_icon="🏛️")

# --- 2. CONNESSIONE DATABASE ---
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except:
        return None

supabase = init_connection()

# --- 3. MOTORE REPORT BANCARIO (PDF) ---
def create_banking_report(azienda, rating, m):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "COIN-NEXUS | FINANCIAL INTELLIGENCE REPORT", ln=True, align='C')
    pdf.ln(10)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 15, f"VALUTAZIONE FINALE: {rating}", 1, 1, 'C', True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "1. SNAPSHOT FINANZIARIO", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f"Azienda: {azienda}", ln=True)
    pdf.cell(0, 8, f"Ricavi: EUR {m['rev']:,.0f}", ln=True)
    pdf.cell(0, 8, f"EBITDA: EUR {m['ebitda']:,.0f}", ln=True)
    pdf.cell(0, 8, f"Indice DSCR: {m['dscr']:.2f}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "2. STRESS TEST (SCENARIO -20%)", ln=True)
    pdf.set_font("Arial", '', 10)
    stress_ebitda = (m['rev'] * 0.8) - (m['rev'] - m['ebitda'])
    resilienza = "ALTA" if stress_ebitda > 0 else "CRITICA"
    pdf.multi_cell(0, 8, f"In caso di calo del fatturato del 20%, l'EBITDA scenderebbe a EUR {stress_ebitda:,.0f}. Resilienza: {resilienza}.")
    pdf.ln(10)
    verdetto = "CREDITO APPROVATO" if rating != "CCC" else "REVISIONE RICHIESTA"
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 15, f"DECISIONE FINALE: {verdetto}", 0, 1, 'C')
    return pdf.output(dest='S').encode('latin-1')

# --- 4. LOGICA DI AUDIT ---
def perform_audit(rev, costs, debt):
    ebitda = rev - costs
    dscr = ebitda / (debt if debt > 0 else 1)
    if dscr > 2.2: rating = "AAA"
    elif dscr > 1.2: rating = "BBB"
    else: rating = "CCC"
    return rating, dscr, ebitda

# --- 5. INTERFACCIA ---
st.title("🏛️ Coin-Nexus | Banking Terminal")

with st.sidebar:
    st.header("📥 Input Dati ERP")
    comp = st.text_input("Ragione Sociale", "Azienda Target S.p.A.")
    r = st.number_input("Ricavi (€)", value=1000000)
    c = st.number_input("Costi (€)", value=800000)
    d = st.number_input("Debito (€)", value=200000)
    btn = st.button("🚀 ESEGUI ANALISI BANKING")

if btn:
    rating, dscr, ebitda = perform_audit(r, c, d)
    metrics = {'rev': r, 'ebitda': ebitda, 'dscr': dscr}
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Rating", rating)
    m2.metric("DSCR", f"{dscr:.2f}")
    m3.metric("EBITDA", f"€{ebitda:,.0f}")

    st.divider()
    g1, g2 = st.columns(2)
    with g1:
        # Gauge Chart Corretto
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number", 
            value=dscr,
            gauge={
                'axis': {'range': [0, 5]},
                'bar': {'color': "#00f2ff"},
                'steps': [
                    {'range': [0, 1.2], 'color': "#ff4b4b"},
                    {'range': [1.2, 2.5], 'color': "#ffa500"},
                    {'range': [2.5, 5], 'color': "#00cc66"}
                ]
            }
        ))
        fig_g.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
        st.plotly_chart(fig_g, use_container_width=True)
        
    with g2:
        # Radar Chart
        fig_r = go.Figure(go.Scatterpolar(
            r=[80, 70, dscr*20, 90, 85], 
            theta=['Fatturato','Margine','Solvibilita','Leva','Resilienza'], 
            fill='toself', 
            line_color='#00f2ff'
        ))
        fig_r.update_layout(height=300, polar=dict(radialaxis=dict(visible=True, range=[0, 100])), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
        st.plotly_chart(fig_r, use_container_width=True)

    st.divider()
    try:
        pdf_out = create_banking_report(comp, rating, metrics)
        st.download_button("📄 SCARICA REPORT DECISIONALE", data=pdf_out, file_name=f"Report_{comp}.pdf", mime="application/pdf", use_container_width=True)
    except Exception as e:
        st.error(f"Errore PDF: {e}")

    if supabase:
        try:
            supabase.table("audit_reports").insert({"company_name": comp, "rating": rating
