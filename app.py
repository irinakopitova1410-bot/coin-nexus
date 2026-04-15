import streamlit as st
import plotly.graph_objects as go
from supabase import create_client, Client
import pandas as pd
from fpdf import FPDF

# --- 1. SETUP ---
st.set_page_config(page_title="Coin-Nexus Terminal", layout="wide", page_icon="🏛️")

@st.cache_resource
def init_connection():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except:
        return None

supabase = init_connection()

# --- 2. PDF ENGINE ---
def create_banking_report(azienda, rating, m):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "COIN-NEXUS | FINANCIAL REPORT", ln=True, align='C')
    pdf.ln(10)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 15, f"RATING: {rating}", 1, 1, 'C', True)
    pdf.ln(5)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f"Azienda: {azienda}", ln=True)
    pdf.cell(0, 8, f"Ricavi: EUR {m['rev']:,.0f}", ln=True)
    pdf.cell(0, 8, f"EBITDA: EUR {m['ebitda']:,.0f}", ln=True)
    pdf.cell(0, 8, f"DSCR: {m['dscr']:.2f}", ln=True)
    pdf.ln(5)
    stress_ebitda = (m['rev'] * 0.8) - (m['rev'] - m['ebitda'])
    res = "ALTA" if stress_ebitda > 0 else "CRITICA"
    pdf.multi_cell(0, 8, f"Stress Test (-20%): EBITDA stimato EUR {stress_ebitda:,.0f}. Resilienza: {res}.")
    return pdf.output(dest='S').encode('latin-1')

# --- 3. AUDIT LOGIC ---
def perform_audit(rev, costs, debt):
    ebitda = rev - costs
    dscr = ebitda / (debt if debt > 0 else 1)
    if dscr > 2.2: r = "AAA"
    elif dscr > 1.2: r = "BBB"
    else: r = "CCC"
    return r, dscr, ebitda

# --- 4. UI ---
st.title("🏛️ Coin-Nexus | Banking Terminal")

with st.sidebar:
    st.header("📥 Input Dati")
    comp = st.text_input("Ragione Sociale", "Azienda Target S.p.A.")
    r = st.number_input("Ricavi (€)", value=1000000)
    c = st.number_input("Costi (€)", value=800000)
    d = st.number_input("Debito (€)", value=200000)
    btn = st.button("🚀 GENERA ANALISI")

if btn:
    rating, dscr, ebitda = perform_audit(r, c, d)
    metrics = {'rev': r, 'ebitda': ebitda, 'dscr': dscr}
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Rating", rating)
    col2.metric("DSCR", f"{dscr:.2f}")
    col3.metric("EBITDA", f"€{ebitda:,.0f}")

    st.divider()
    g1, g2 = st.columns(2)
    with g1:
        fig_g = go.Figure(go.Indicator(mode="gauge+number", value=dscr, gauge={'axis':{'range':[0,5]}, 'bar':{'color':"#00f2ff"}, 'steps':[{'range':[0,1.2],'color':"#ff4b4b"},{'range':[1.2,2.5],'color':"#ffa500"},{'range':[2.5,5],'color':"#00cc66"}]}))
        fig_g.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', font={'color':"white"})
        st.plotly_chart(fig_g, use_container_width=True)
    with g2:
        fig_r = go.Figure(go.Scatterpolar(r=[80, 70, dscr*20, 90, 85], theta=['Fatturato','Margine','Solvibilita','Leva','Resilienza'], fill='toself', line_color='#00f2ff'))
        fig_r.update_layout(height=250, polar=dict(radialaxis=dict(visible=False, range=[0, 100])), paper_bgcolor='rgba(0,0,0,0)', font={'color':"white"})
        st.plotly_chart(fig_r, use_container_width=True)

    st.divider()
    try:
        pdf_out = create_banking_report(comp, rating
