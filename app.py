import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from fpdf import FPDF

# --- SETUP PROFESSIONALE ---
st.set_page_config(page_title="Coin-Nexus | Banking Audit", layout="wide")

def calcola_capacita_credito(ebitda, debito_attuale, dscr):
    # Logica bancaria: quanta nuova finanza può reggere l'azienda?
    if dscr > 1.5:
        potenziale = ebitda * 3 # Può chiedere circa 3 volte l'EBITDA
        return potenziale
    return 0

# --- MOTORE PDF AUDIT ---
def genera_report_legale(dati):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "AUDIT DI PRE-FATTIBILITA BANCARIA", ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, f"Rif. Normativo: Adeguati Assetti Org. (Art. 2086 c.c.)", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Analisi per: {dati['nome']}", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 10, f"Sulla base dei dati forniti, l'azienda presenta un DSCR di {dati['dscr']:.2f}. "
                          f"Il Rating calcolato secondo i modelli interni di pre-valutazione è: {dati['score']}.")
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, "CAPACITA DI NUOVO CREDITO STIMATA:", ln=True)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(0, 150, 0)
    pdf.cell(0, 10, f"EUR {dati['potenziale']:,.0f}", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# --- UI ---
st.title("🏛️ Coin-Nexus Audit | Bankability Gateway")
st.info("Strumento di analisi per la Centrale Rischi e l'accesso al credito")

t1, t2 = st.tabs(["📊 Analisi Bancaria", "📜 Report Legale"])

with t1:
    col1, col2 = st.columns([1, 2])
    with col1:
        nome = st.text_input("Azienda", "S.p.A. Target")
        rev = st.number_input("Ricavi Annuì", value=5000000)
        ebitda = st.number_input("EBITDA (MOL)", value=800000)
        pfn = st.number_input("Debito Finanziario Totale", value=1200000)
        oneri = st.number_input("Oneri Finanziari Annuì", value=50000)
        
        dscr = ebitda / (oneri + (pfn/5)) # Formula semplificata DSCR a 5 anni
        score = "ECCELLENTE" if dscr > 2.5 else "SOSTENIBILE" if dscr > 1.2 else "VULNERABILE"
        potenziale = calcola_capacita_credito(ebitda, pfn, dscr)
        
    with col2:
        st.metric("Rating di Sostenibilità", score)
        st.metric("DSCR (Capacità di rimborso)", f"{dscr:.2f}")
        
        fig = go.Figure(go.Indicator(mode="gauge+number", value=dscr,
            gauge={'axis':{'range':[0, 5]}, 'bar':{'color': "green" if dscr > 1.2 else "red"}}))
        st.plotly_chart(fig, use_container_width=True)

with t2:
    st.subheader("Generazione Dossier per la Banca")
    st.write("Questo documento integra i requisiti per la richiesta di nuovo affidamento.")
    
    dati_report = {
        'nome': nome, 'dscr': dscr, 'score': score, 'potenziale': potenziale
    }
    
    if st.button("GENERA DOSSIER AUDIT"):
        pdf_file = genera_report_legale(dati_report)
        st.download_button("📥 Scarica Report PDF", pdf_file, f"Audit_{nome}.pdf", "application/pdf")
