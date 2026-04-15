import streamlit as st
import plotly.graph_objects as go
from scoring import NexusScorer
from fpdf import FPDF

# Configurazione Pagina
st.set_page_config(page_title="Coin-Nexus Enterprise", layout="wide", page_icon="🏛️")

# Funzione Generazione PDF Reale
def generate_pdf_report(company, rating, mat, bep, safety):
    pdf = FPDF()
    pdf.add_page()
    # Header
    pdf.set_fill_color(13, 17, 23)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 20, "COIN-NEXUS | EXECUTIVE AUDIT DOSSIER", 0, 1, 'C')
    
    # Dati
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.ln(20)
    pdf.cell(0, 10, f"Analisi per: {company}", 0, 1)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 10, f"Rating Finale: {rating}", 0, 1)
    pdf.cell(0, 10, f"Soglia ISA 320: EUR {mat:,.0f}", 0, 1)
    pdf.cell(0, 10, f"Punto di Pareggio: EUR {bep:,.0f}", 0, 1)
    pdf.cell(0, 10, f"Margine di Sicurezza: {safety}%", 0, 1)
    
    # Disclaimer
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 9)
    pdf.multi_cell(0, 5, "Documento generato via AI-Protocol Coin-Nexus. Valido per istruttoria DocFinance.")
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACCIA ---
with st.sidebar:
    st.title("📥 ERP Input")
    company_name = st.text_input("Azienda", "Coin-Nexus Partner S.r.l.")
    rev = st.number_input("Ricavi (€)", value=5450000)
    costs = st.number_input("Costi (€)", value=4500000)
    debt = st.number_input("Debito (€)", value=1200000)
    run_audit = st.button("🚀 ESEGUI AUDIT")

st.title("🏛️ Coin-Nexus | Risk Terminal")

if run_audit:
    scorer = NexusScorer(rev, costs, debt)
    mat = scorer.calculate_isa_320()
    bep, safety = scorer.calculate_bep()
    rating, desc = scorer.get_nexus_rating()

    # Metrics Row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rating Basel IV", rating, desc)
    c2.metric("ISA 320", f"€{mat:,.0f}")
    c3.metric("BEP", f"€{bep:,.0f}")
    c4.metric("Sicurezza", f"{safety}%")
# Sotto il tasto di download, aggiungiamo il salvataggio automatico
if st.button("💾 Salva nel mio Archivio Cloud"):
    try:
        report_data = {
            "company_name": company_name,
            "rating": rating,
            "revenue": rev,
            "costs": costs,
            "debt": debt,
            "isa_320_threshold": mat,
            "bep": bep,
            "safety_margin": safety,
            "user_id": st.session_state.user.id # Richiede il login attivo
        }
        supabase.table("audit_reports").insert(report_data).execute()
        st.success("Analisi salvata con successo nel tuo account!")
    except Exception as e:
        st.error(f"Errore nel salvataggio: {e}")
    # GRAFICI PROFESSIONALI
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("🎯 Posizionamento Asset")
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[95, 80, 85, 90, 88],
            theta=['Liquidità', 'Solvibilità', 'Efficienza', 'Resilienza', 'Rating'],
            fill='toself', name='Azienda', line_color='#00f2ff'
        ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), template="plotly_dark")
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_r:
        st.subheader("📊 Struttura Costi/Ricavi")
        fig_bar = go.Figure(go.Bar(
            x=['Ricavi', 'Costi', 'EBITDA'],
            y=[rev, costs, rev-costs],
            marker_color=['#00f2ff', '#ff4b4b', '#00ff00']
        ))
        fig_bar.update_layout(template="plotly_dark")
        st.plotly_chart(fig_bar, use_container_width=True)

    # DOWNLOAD PDF
    st.divider()
    pdf_bytes = generate_pdf_report(company_name, rating, mat, bep, safety)
    
    st.download_button(
        label="📥 SCARICA REPORT CERTIFICATO (PDF)",
        data=pdf_bytes,
        file_name=f"Audit_{company_name}.pdf",
        mime="application/pdf"
    )
else:
    st.info("👈 Configura i parametri ERP a sinistra e avvia l'audit per visualizzare i grafici e scaricare il report.")
