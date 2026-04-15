import streamlit as st
import plotly.graph_objects as go
from supabase import create_client, Client
import pandas as pd
from fpdf import FPDF

# --- 1. CORE SETUP ---
st.set_page_config(page_title="Coin-Nexus SaaS", layout="wide", page_icon="🏛️")

@st.cache_resource
def init_db():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except: return None

db = init_db()

# --- 2. BANKING REPORT ENGINE ---
def get_pdf(az, rt, m):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"FINANCIAL DOSSIER: {az}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"RATING DECISIONALE: {rt}", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, f"Ricavi: EUR {m['r']:,.0f}", ln=True)
    pdf.cell(0, 7, f"EBITDA: EUR {m['e']:,.0f}", ln=True)
    pdf.cell(0, 7, f"DSCR: {m['d']:.2f}", ln=True)
    # Stress Test Logic
    st_ebitda = (m['r'] * 0.8) - (m['r'] - m['e'])
    res = "ALTA" if st_ebitda > 0 else "CRITICA"
    pdf.ln(5)
    pdf.multi_cell(0, 7, f"STRESS TEST SCENARIO (-20% Ricavi): EBITDA stimato EUR {st_ebitda:,.0f}. Resilienza: {res}.")
    return pdf.output(dest='S').encode('latin-1')

# --- 3. UI & LOGIC ---
st.title("🏛️ Coin-Nexus | Risk Intelligence Terminal")

with st.sidebar:
    st.header("🏢 Input Azienda")
    name = st.text_input("Ragione Sociale", "Azienda S.r.l.")
    rev = st.number_input("Ricavi (€)", value=1000000)
    cost = st.number_input("Costi (€)", value=850000)
    debt = st.number_input("Debito (€)", value=100000)
    trigger = st.button("🚀 ESEGUI AUDIT")

if trigger:
    # Calcoli Professionali
    ebitda = rev - cost
    dscr = ebitda / (debt if debt > 0 else 1)
    score = "AAA" if dscr > 2.2 else "BBB" if dscr > 1.2 else "CCC"
    data_bundle = {'r': rev, 'e': ebitda, 'd': dscr}
    
    # Dashboard Metriche
    c1, c2, c3 = st.columns(3)
    c1.metric("Score", score)
    c2.metric("DSCR", f"{dscr:.2f}")
    c3.metric("EBITDA", f"€{ebitda:,.0f}")

    # Visualizzazione Grafica
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=dscr,
        gauge={'axis':{'range':[0, 5]}, 'bar':{'color':"#00f2ff"},
               'steps':[{'range':[0, 1.2], 'color':"red"}, {'range':[1.2, 5], 'color':"green"}]}))
    fig.update_layout(height=280, paper_bgcolor='rgba(0,0,0,0)', font={'color':"white"})
    st.plotly_chart(fig, use_container_width=True)

    # Report & Database
    st.divider()
    try:
        report = get_pdf(name, score, data_bundle)
        st.download_button("📥 SCARICA REPORT BANCARIO", report, f"Nexus_{name}.pdf", "application/pdf")
        if db:
            db.table("audit_reports").insert({"company_name": name, "rating": score, "revenue": rev}).execute()
            st.success("Dossier archiviato nel Cloud.")
    except Exception as e:
        st.error(f"Erro
