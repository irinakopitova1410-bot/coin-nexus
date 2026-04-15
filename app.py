import streamlit as st
import plotly.graph_objects as go
from supabase import create_client, Client
import pandas as pd
from fpdf import FPDF

# --- 1. SETUP & CONNESSIONE ---
st.set_page_config(page_title="Coin-Nexus Terminal", layout="wide")

try:
    # Recupero credenziali dai Secrets di Streamlit
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except:
    st.error("Configura SUPABASE_URL e SUPABASE_KEY nei Secrets di Streamlit Cloud!")
    st.stop()

# --- 2. FUNZIONE PER IL PDF ---
def genera_pdf(nome, rating, dati):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"COIN-NEXUS AUDIT: {nome.upper()}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Rating Assegnato: {rating}", ln=True)
    pdf.cell(0, 10, f"Ricavi: EUR {dati['rev']:,.0f}", ln=True)
    pdf.cell(0, 10, f"DSCR: {dati['dscr']:.2f}", ln=True)
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
