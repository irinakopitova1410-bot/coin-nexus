import streamlit as st
import plotly.graph_objects as go
from supabase import create_client, Client
import pandas as pd
from fpdf import FPDF

# --- 1. SETUP & CONNESSIONE ---
st.set_page_config(page_title="Coin-Nexus Terminal", layout="wide")

try:
    # Recupero credenziali dai Secrets di Streamlit
    url = st.secrets["https://ipmttldwfsxuubugiyir.supabase.co"]
    key = st.secrets["sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos"]
    supabase = create_client(url, key)
except:
    st.error("Configura SUPABASE_URL e SUPABASE_KEY nei Secrets di Streamlit Cloud!")
    st.stop()

def create_banking_report(company, rating, metrics):
    pdf = FPDF()
    pdf.add_page()
    
    # --- 1. HEADER ISTITUZIONALE ---
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "COIN-NEXUS FINANCIAL INTELLIGENCE", ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, "Confidential Credit Assessment Report", ln=True, align='C')
    pdf.ln(10)

    # --- 2. EXECUTIVE SUMMARY (Decision Box) ---
    pdf.set_fill_color(245, 245, 245)
    pdf.rect(10, 35, 190, 30, 'F')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Azienda: {company.upper()}", ln=True)
    pdf.set_font("Arial", 'B', 15)
    pdf.set_text_color(0, 100, 0) if rating == "AAA" else pdf.set_text_color(200, 0, 0)
    pdf.cell(0, 10, f"SCORE FINALE: {rating} / 100", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

    # --- 3. FINANCIAL SNAPSHOT (Tabella Pura) ---
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, "SECTION 1: FINANCIAL SNAPSHOT", ln=True)
    pdf.set_font("Arial", '', 10)
    
    rows = [
        ["Ricavi (LTM)", f"EUR {metrics['rev']:,.0f}"],
        ["EBITDA", f"EUR {metrics['ebitda']:,.0f}"],
        ["DSCR (Debt Cover)", f"{metrics['dscr']:.2f}"],
        ["Net Working Capital", "Analisi in corso..."]
    ]
    for row in rows:
        pdf.cell(95, 8, row[0], 1)
        pdf.cell(95, 8, row[1], 1, 1, 'R')
    pdf.ln(5)

    # --- 4. AI SCORE EXPLANATION (Il "Perché") ---
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, "SECTION 2: AI SCORE EXPLANATION", ln=True)
    pdf.set_font("Arial", '', 10)
    
    # Logica di spiegazione automatica
    explanations = []
    if metrics['dscr'] > 1.5: explanations.append("[+] Solida capacita' di rimborso del debito (+20 pts)")
    else: explanations.append("[-] Flusso di cassa teso rispetto alle scadenze (-15 pts)")
    
    if (metrics['ebitda']/metrics['rev']) > 0.15: explanations.append("[+] Elevata marginalita' operativa (+15 pts)")
    
    for line in explanations:
        pdf.cell(0, 7, line, ln=True)
    pdf.ln(5)

    # --- 5. STRESS TEST SCENARIO (-20%) ---
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, "SECTION 3: STRESS TEST (SCENARIO AVVERSO -20%)", ln=True)
    pdf.set_font("Arial", '', 10)
    
    stress_rev = metrics['rev'] * 0.8
    stress_ebitda = stress_rev - (metrics['rev'] - metrics['ebitda'])
    resilienza = "ALTA" if stress_ebitda > 0 else "CRITICA"
    
    pdf.multi_cell(0, 7, f"Simulazione contrazione ricavi: In caso di calo del 20% del fatturato, l'azienda genererebbe un EBITDA di EUR {stress_ebitda:,.0f}. Grado di resilienza: {resilienza}.")

    # --- 6. FINAL VERDICT (The "Verdict") ---
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(0, 0, 0)
    pdf.set_text_color(255, 255, 255)
    verdict = "CREDIT APPROVED" if rating != "CCC" else "CREDIT REJECTED / REVIEW REQUIRED"
    pdf.cell(0, 15, f"FINAL VERDICT: {verdict}", 0, 1, 'C', True)

    return pdf.output(dest='S').encode('latin-1')
# --- 3. INTERFACCIA UTENTE ---
st.title("🏛️ Coin-Nexus | Financial Terminal")

with st.sidebar:
    st.header("Dati Aziendali")
    azienda = st.text_input("Ragione Sociale", "Azienda S.r.l.")
    rev = st.number_input("Ricavi (€)", value=1000000)
    costi = st.number_input("Costi (€)", value=800000)
    debito = st.number_input("Debito (€)", value=200000)
    tasto = st.button("🚀 GENERA ANALISI")

if tasto:
    # Calcoli immediati
    ebitda = rev - costi
    dscr = ebitda / (debito if debito > 0 else 1)
    voto = "AAA" if dscr > 2.0 else "BBB" if dscr > 1.1 else "CCC"
    
    # Metriche a video
    c1, c2, c3 = st.columns(3)
    c1.metric("Rating", voto)
    c2.metric("EBITDA", f"€{ebitda:,.0f}")
    c3.metric("DSCR", f"{dscr:.2f}")

    # Generazione PDF
    info = {'rev': rev, 'ebitda': ebitda, 'dscr': dscr}
    pdf_file = genera_pdf(azienda, voto, info)
    
    st.download_button(
        label="📄 SCARICA REPORT PDF",
        data=pdf_file,
        file_name=f"Report_{azienda}.pdf",
        mime="application/pdf"
    )

    # Salvataggio su Supabase
    try:
        supabase.table("audit_reports").insert({
            "company_name": azienda, "rating": voto, "revenue": rev
        }).execute()
        st.success("Dati salvati nel Cloud!")
    except:
        st.info("Database non aggiornato.")

# --- 4. VISUALIZZAZIONE STORICO ---
st.divider()
st.subheader("📑 Ultime Analisi nel Database")
try:
    res = supabase.table("audit_reports").select("*").order("created_at", desc=True).limit(5).execute()
    if res.data:
        st.table(pd.DataFrame(res.data)[['company_name', 'rating', 'revenue']])
except:
    st.write("Nessun dato ancora disponibile.")
