import streamlit as st
import plotly.graph_objects as go
from supabase import create_client, Client
from fpdf import FPDF
import pandas as pd

# --- SETUP PAGINA ---
st.set_page_config(page_title="Coin-Nexus SaaS", layout="wide", page_icon="🏛️")

# --- CONNESSIONE DATABASE ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except:
    st.error("Configura i Secrets (URL/KEY) su Streamlit Cloud!")
    st.stop()

# --- LOGICA FINANZIARIA ---
def get_audit(rev, costs, debt):
    ebitda = rev - costs
    dscr = ebitda / (debt if debt > 0 else 1)
    isa_320 = max(ebitda * 0.05, rev * 0.01)
    safety = round(((rev - costs) / rev) * 100, 2)
    rating = "AAA" if dscr > 2.5 else "BBB" if dscr > 1.2 else "CCC"
    return rating, isa_320, dscr, safety

# --- FUNZIONE PDF ---
def create_pdf(company, rating, isa, dscr, safety):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "COIN-NEXUS FINANCIAL AUDIT", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Azienda: {company}", ln=True)
    pdf.cell(0, 10, f"Rating: {rating}", ln=True)
    pdf.cell(0, 10, f"Soglia ISA 320: EUR {isa:,.0f}", ln=True)
    pdf.cell(0, 10, f"DSCR: {dscr:.2f}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACCIA ---
st.title("🏛️ Coin-Nexus | Risk & Rating Terminal")
st.markdown("---")

with st.sidebar:
    st.header("📥 ERP Input")
    company = st.text_input("Ragione Sociale", "Azienda Target S.p.A.")
    rev = st.number_input("Ricavi (€)", value=5000000)
    costs = st.number_input("Costi (€)", value=4200000)
    debt = st.number_input("Debito (€)", value=1000000)
    run = st.button("🚀 GENERA AUDIT")

if run:
    rating, isa, dscr, safety = get_audit(rev, costs, debt)
    
    # 1. KPI ROW
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rating", rating)
    col2.metric("ISA 320", f"€{isa:,.0f}")
    col3.metric("DSCR", f"{dscr:.2f}")
    col4.metric("Margine", f"{safety}%")

    # 2. GRAFICI
    c_left, c_right = st.columns(2)
    
    with c_left:
        # Gauge Chart
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = dscr,
            title = {'text': "Creditworthiness (DSCR)"},
            gauge = {'axis': {'range': [0, 5]}, 'bar': {'color': "cyan"}}
        ))
        fig_gauge.update_layout(template="plotly_dark", height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)

    with c_right:
        # Radar Chart
        fig_radar = go.Figure(go.Scatterpolar(
            r=[85, 90, 70, 80, 75],
            theta=['Liquidità','Solvibilità','Efficienza','Resilienza','Rating'],
            fill='toself', line_color='cyan'
        ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), template="plotly_dark", height=300)
        st.plotly_chart(fig_radar, use_container_width=True)

    # 3. SALVATAGGIO & PDF
    pdf_file = create_pdf(company, rating, isa, dscr, safety)
    st.download_button("📥 SCARICA REPORT CERTIFICATO", pdf_file, f"Audit_{company}.pdf", "application/pdf")
    
    try:
        supabase.table("audit_reports").insert({"company_name": company, "rating": rating, "revenue": rev}).execute()
        st.success("Analisi salvata nel Cloud.")
    except:
        st.warning("Database offline: salvataggio non riuscito.")

# --- STORICO CLOUD ---
st.divider()
st.subheader("📑 Archivio Audit Real-Time")
