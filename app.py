import streamlit as st
import plotly.graph_objects as go
from supabase import create_client, Client
import pandas as pd
from fpdf import FPDF

# --- 1. SETUP ---
st.set_page_config(page_title="Coin-Nexus Terminal", layout="wide")

@st.cache_resource
def init_connection():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except: return None

supabase = init_connection()

# --- 2. MOTORE PDF ---
def create_banking_report(az, rt, m):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"COIN-NEXUS REPORT: {az}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"RATING FINALE: {rt}", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, f"Ricavi: EUR {m['rev']:,.0f}", ln=True)
    pdf.cell(0, 7, f"EBITDA: EUR {m['ebitda']:,.0f}", ln=True)
    pdf.cell(0, 7, f"DSCR: {m['dscr']:.2f}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- 3. LOGICA ---
def perform_audit(rev, costs, debt):
    ebitda = rev - costs
    dscr = ebitda / (debt if debt > 0 else 1)
    if dscr > 2.2: r = "AAA"
    elif dscr > 1.2: r = "BBB"
    else: r = "CCC"
    return r, dscr, ebitda

# --- 4. UI ---
st.title("🏛️ Coin-Nexus | Financial Terminal")

with st.sidebar:
    st.header("Input Dati")
    az = st.text_input("Azienda", "Azienda Target S.p.A.")
    r = st.number_input("Ricavi (€)", value=1000000)
    c = st.number_input("Costi (€)", value=800000)
    d = st.number_input("Debito (€)", value=200000)
    go_btn = st.button("🚀 ESEGUI ANALISI")

if go_btn:
    rating, dscr, ebitda = perform_audit(r, c, d)
    m_bundle = {'rev': r, 'ebitda': ebitda, 'dscr': dscr}
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Rating", rating)
    c2.metric("DSCR", f"{dscr:.2f}")
    c3.metric("EBITDA", f"€{ebitda:,.0f}")

    st.divider()
    # Grafico Gauge Semplificato
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=dscr,
        gauge={'axis':{'range':[0,5]}, 'bar':{'color':"#00f2ff"},
               'steps':[{'range':[0,1.2],'color':"red"},{'range':[1.2,5],'color':"green"}]}))
    fig.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', font={'color':"white"})
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    try:
        pdf_data = create_banking_report(az, rating, m_bundle)
        st.download_button("📄 SCARICA REPORT", pdf_data, f"Nexus_{az}.pdf", "application/pdf")
    except Exception as e:
        st.error(f"Errore PDF: {e}")

    if supabase:
        try:
            supabase.table("audit_reports").insert({"company_name": az, "rating": rating, "revenue": r}).execute()
        except: pass

st.divider()
if supabase:
    try:
        res = supabase.table("audit_reports").select("company_name, rating, revenue").order("created_at", desc=True).limit(3).execute()
        if res.data: st.table(res.data)
    except: st.info("Database in aggiornamento...")
