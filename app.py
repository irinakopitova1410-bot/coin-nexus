import streamlit as st
import plotly.graph_objects as go
from supabase import create_client
import pandas as pd
from fpdf import FPDF

st.set_page_config(page_title="Coin-Nexus", layout="wide")

@st.cache_resource
def init_db():
    try: return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except: return None

db = init_db()

def get_pdf(az, rt, m):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"REPORT: {az}", ln=1, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"RATING: {rt}", ln=1)
    pdf.cell(0, 10, f"Ricavi: {m['r']}", ln=1)
    pdf.cell(0, 10, f"DSCR: {m['d']:.2f}", ln=1)
    return pdf.output(dest='S').encode('latin-1')

st.title("🏛️ Coin-Nexus Terminal")

with st.sidebar:
    name = st.text_input("Azienda", "Target Srl")
    rev = st.number_input("Ricavi", value=1000000)
    cost = st.number_input("Costi", value=800000)
    debt = st.number_input("Debito", value=200000)
    run = st.button("ESEGUI")

if run:
    ebitda = rev - cost
    dscr = ebitda / (debt if debt > 0 else 1)
    score = "AAA" if dscr > 2.2 else "BBB" if dscr > 1.2 else "CCC"
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Score", score)
    c2.metric("DSCR", f"{dscr:.2f}")
    c3.metric("EBITDA", f"{ebitda}")

    fig = go.Figure(go.Indicator(mode="gauge+number", value=dscr, gauge={'axis':{'range':[0,5]}, 'steps':[{'range':[0,1.2],'color':"red"},{'range':[1.2,5],'color':"green"}]}))
    fig.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', font={'color':"white"})
    st.plotly_chart(fig, use_container_width=True)

    try:
        pdf = get_pdf(name, score, {'r':rev, 'e':ebitda, 'd':dscr})
        st.download_button("SCARICA PDF", pdf, "Report.pdf", "application/pdf")
        if db: db.table("audit_reports").insert({"company_name":name,"rating":score,"revenue":rev}).execute()
    except Exception as e: st.error("Errore export")

st.divider()
if db:
    try:
        res = db.table("audit_reports").select("company_name,rating").order("created_at",desc=True).limit(3).execute()
        if res.data: st.table(res.data)
    except: st.info("DB offline")
