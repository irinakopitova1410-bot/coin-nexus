import streamlit as st
import plotly.graph_objects as go
from scoring import NexusScorer
from fpdf import FPDF
import base64

# Funzione per generare il PDF fisicamente
def create_pdf(company, rating, mat, bep, safety):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "COIN-NEXUS | EXECUTIVE AUDIT REPORT", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Ragione Sociale: {company}", ln=True)
    pdf.cell(200, 10, f"Rating Basel IV: {rating}", ln=True)
    pdf.cell(200, 10, f"Soglia Materialita (ISA 320): EUR {mat:,.2f}", ln=True)
    pdf.cell(200, 10, f"Punto di Pareggio (BEP): EUR {bep:,.2f}", ln=True)
    pdf.cell(200, 10, f"Margine di Sicurezza: {safety}%", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, "Esito: Il protocollo Telepass Bancario e' attivo. L'asset e' pronto per la cartolarizzazione.")
    return pdf.output(dest='S').encode('latin-1')

st.set_page_config(page_title="Coin-Nexus Terminal", layout="wide")

with st.sidebar:
    st.header("📊 ERP Input")
    company = st.text_input("Azienda", "Azienda Target S.r.l.")
    rev = st.number_input("Ricavi (€)", value=5450000)
    costs = st.number_input("Costi (€)", value=4500000)
    debt = st.number_input("Debito (€)", value=1200000)
    run = st.button("🚀 ESEGUI AUDIT")

st.title("🏛️ Coin-Nexus | Risk Terminal")

if run:
    scorer = NexusScorer(rev, costs, debt)
    mat = scorer.calculate_isa_320()
    bep, safety = scorer.calculate_bep()
    rating, desc = scorer.get_nexus_rating()

    # Visualizzazione KPI
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rating", rating, desc)
    c2.metric("ISA 320", f"€{mat:,.0f}")
    c3.metric("BEP", f"€{bep:,.0f}")
    c4.metric("Sicurezza", f"{safety}%")

    # Generazione PDF reale
    pdf_data = create_pdf(company, rating, mat, bep, safety)
    
    st.divider()
    st.download_button(
        label="📥 SCARICA REPORT CERTIFICATO (PDF)",
        data=pdf_data,
        file_name=f"Audit_{company}.pdf",
        mime="application/pdf"
    )
    st.success("Report generato con successo. Clicca sopra per scaricare.")
