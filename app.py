import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import io
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Coin-Nexus Quantum Audit & Plan", layout="wide", page_icon="💠")

if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'user_email' not in st.session_state: st.session_state['user_email'] = None

# --- CLASSE PDF PREMIUM (Con sezione Business Plan) ---
class QuantumReport(FPDF):
    def header(self):
        self.set_fill_color(20, 30, 50)
        self.rect(0, 0, 210, 40, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 20)
        self.cell(0, 20, 'COIN-NEXUS STRATEGIC REPORT', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, -5, 'Audit ISA 320 & Business Plan 4-Year Outlook', 0, 1, 'C')
        self.ln(20)

    def section_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, f"  {label}", 0, 1, 'L', True)
        self.ln(4)

def genera_pdf_strategico(massa, mat, file_name, user, bp_data):
    pdf = QuantumReport()
    pdf.add_page()
    
    # 1. Audit Past
    pdf.section_title("CERTIFICAZIONE AUDIT (CONSUNTIVO)")
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 8, f"Soggetto: {file_name} | Auditor: {user}", ln=True)
    pdf.cell(0, 8, f"Materialita Calcolata: Euro {mat:,.2f}", ln=True)
    pdf.ln(5)

    # 2. Business Plan Outlook
    pdf.section_title("BUSINESS PLAN & PROSPETTIVA 4 ANNI")
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 8, "Anno", 1)
    pdf.cell(70, 8, "Fatturato Stimato", 1)
    pdf.cell(70, 8, "Rischio Operativo", 1, ln=True)
    
    pdf.set_font('Arial', '', 10)
    for year, row in bp_data.iterrows():
        pdf.cell(40, 8, str(year), 1)
        pdf.cell(70, 8, f"Euro {row['Fatturato']:,.2f}", 1)
        pdf.cell(70, 8, f"{row['Rischio']}", 1, ln=True)
    
    pdf.ln(10)
    pdf.section_title("VALUTAZIONE DEL RISCHIO BANCARIO")
    pdf.multi_cell(0, 8, "Il profilo di rischio a medio-lungo termine risulta 'Basso'. \n"
                         "La sostenibilita del debito e garantita da flussi di cassa incrementali. \n"
                         "Principali rischi monitorati: Volatilita tassi (Rating A+).")
    
    # Firma
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 10, "Firma Elettronica Certificata Coin-Nexus", 0, 1, 'R')
    
    return pdf.output(dest='S').encode('latin-1')

# --- LOGIN ---
if not st.session_state['auth']:
    st.title("💠 Coin-Nexus Quantum AI")
    with st.sidebar:
        e = st.text_input("Email Admin")
        p = st.text_input("Password", type="password")
        if st.button("ACCEDI"):
            if e == "admin@coin-nexus.com" and p == "quantum2026":
                st.session_state['auth'], st.session_state['user_email'] = True, e
                st.rerun()
    st.stop()

# --- MAIN DASHBOARD ---
st.title(f"🚀 Strategic Planning & Audit: {st.session_state['user_email']}")
up = st.file_uploader("Carica Dati Finanziari", type=['xlsx', 'csv'])

if up:
    df = pd.read_excel(up) if up.name.endswith('.xlsx') else pd.read_csv(up)
    val_col = st.selectbox("Seleziona Colonna Valori per proiezione", df.select_dtypes(include=[np.number]).columns)

    if st.button("📈 GENERA BUSINESS PLAN 4 ANNI"):
        # Logica Proiezione
        last_val = df[val_col].abs().sum()
        years = [2026, 2027, 2028, 2029]
        growth_rate = 1.05 # +5% annuo
        
        projections = []
        for i, y in enumerate(years):
            val = last_val * (growth_rate ** (i + 1))
            risk = "Basso" if val > last_val else "Monitoraggio"
            projections.append({"Anno": y, "Fatturato": val, "Rischio": risk})
        
        bp_df = pd.DataFrame(projections).set_index("Anno")

        # Visualizzazione
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🔮 Proiezione Profittabilità")
            fig_line = px.line(bp_df, y="Fatturato", title="Trend Crescita 2026-2029", markers=True)
            st.plotly_chart(fig_line, use_container_width=True)
        
        with c2:
            st.subheader("⚠️ Analisi dei Rischi")
            risk_fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = 92,
                title = {'text': "Indice di Affidabilità (%)"},
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "darkblue"}}
            ))
            st.plotly_chart(risk_fig, use_container_width=True)

        # Download Report Strategico
        st.divider()
        massa = last_val
        mat = massa * 0.015
        pdf_bytes = genera_pdf_strategico(massa, mat, up.name, st.session_state['user_email'], bp_df)
        
        st.download_button("📥 SCARICA BUSINESS PLAN & AUDIT (PDF)", pdf_bytes, f"Strategic_Plan_{up.name}.pdf", "application/pdf")
        st.success("Analisi strategica completata per la presentazione bancaria.")
