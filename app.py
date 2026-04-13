import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime
from sklearn.ensemble import IsolationForest
from supabase import create_client, Client

# --- CONFIGURARE SUPABASE ---
# Înlocuiește cu cheia ta reală "anon public" din Supabase
SUPABASE_URL = "https://ipmttldwfsxuubugiyir.supabase.co"
SUPABASE_KEY = "sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos" 

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Eroare conexiune bază de date: {e}")

# --- LOGICĂ GENERARE PDF PROFESIONAL ---
def genera_pdf_platinum(studio, date_calcul, anomalii_count):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Albastru Professional
    pdf.set_fill_color(0, 51, 102)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_font("Arial", 'B', 22)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(190, 20, "COIN-NEXUS QUANTUM REPORT", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(25)
    
    # Informații Generale
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 8, f"STUDIO / ENTITATE: {studio.upper()}", ln=True)
    pdf.cell(190, 8, f"DATA GENERĂRII: {datetime.date.today().strftime('%d/%m/%Y')}", ln=True)
    pdf.line(10, pdf.get_y()+2, 200, pdf.get_y()+2)
    pdf.ln(10)
    
    # Indicatori Financiari ISA 320
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(190, 10, "1. ANALIZĂ DE RISC ȘI MATERIALITATE (ISA 320)", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.cell(190, 8, f"- Venituri Totale Analizate: EUR {date_calcul['venituri']:,.2f}", ln=True)
    pdf.cell(190, 8, f"- Prag Materialitate (1%): EUR {date_calcul['materialitate']:,.2f}", ln=True)
    pdf.cell(190, 8, f"- Rating Atribuit: {date_calcul['rating']}", ln=True)
    pdf.cell(190, 8, f"- Scor Siguranță AI: {date_calcul['score']:.1f}/100", ln=True)
    
    # Forensic Audit
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(190, 10, "2. AUDIT FORENSIC & ANOMALII AI", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.cell(190, 8, f"- Tranzacții Atipice Detectate: {anomalii_count}", ln=True)
    pdf.ln(15)
    
    # Certificare
    pdf.set_font("Arial", 'I', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(190, 5, "Acest raport este generat automat prin algoritmi de Machine Learning (Isolation Forest) și respectă standardele de raportare ISA. Documentul este destinat uzului profesional pentru evaluarea bonității.")
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAȚĂ STREAMLIT ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM AI", layout="wide", page_icon="💠")

# Sistem de Securitate
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.markdown("<h1 style='text-align: center; color: #00f2ff;'>💠 COIN-NEXUS PLATINUM</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pin = st.text_input("CHIEIE LICENȚĂ CLOUD", type="password")
        if st.button("AUTENTIFICARE"):
            if pin == "PLATINUM2026":
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Acces Refuzat")
    st.stop()

# Dashboard Principal
st.title("💠 Quantum Financial Analytics v3.5")

with st.sidebar:
    st.header("⚙️ Setări Analiză")
    nume_studio = st.text_input("Nume Studio/Bancă", "STUDIO_REVISIONI_H")
    fisier = st.file_uploader("Încarcă Balanță / Extras (Excel/CSV)", type=['xlsx', 'csv'])
    if st.button("LOGOUT"):
        st.session_state["auth"] = False
        st.rerun()

if fisier:
    try:
        # Citire date
        df = pd.read_excel(fisier) if fisier.name.endswith('.xlsx') else pd.read_csv(fisier)
        col_num = df.select_dtypes(include=[np.number]).columns[0]
        
        # Calcule Inteligente
        venituri = df[col_num].sum()
        materialitate = venituri * 0.01
        std_dev = df[col_num].std()
        
        # Scor AI și Rating
        scor_ai = 100 - (min((std_dev / venituri) * 100, 40))
        rating = "A++ (Excelent)" if scor_ai > 85 else "B (Stabil)" if scor_ai > 60 else "C (Risc)"
        
        # Detecție Anomalii AI
        model = IsolationForest(
