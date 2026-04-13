import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import datetime
from sklearn.ensemble import IsolationForest
from supabase import create_client, Client

# --- 1. CONFIGURAZIONE SICURA ---
# Se non hai ancora le chiavi, l'app funzionerà comunque (senza salvare su cloud)
SUPABASE_URL = "https://ipmttldwfsxuubugiyir.supabase.co"
SUPABASE_KEY = "sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos" 

def get_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        return None

client_db = get_supabase()

# --- 2. CLASSE PDF OTTIMIZZATA ---
class QuantumPDF(FPDF):
    def header(self):
        self.set_fill_color(0, 51, 102)
        self.rect(0, 0, 210, 40, 'F')
        self.set_font("Arial", 'B', 20)
        self.set_text_color(255, 255, 255)
        self.cell(190, 20, "COIN-NEXUS QUANTUM CERTIFICATION", ln=True, align='C')
        self.ln(20)

def genera_pdf_certificato(studio, dati, anomalie_count):
    pdf = QuantumPDF()
    pdf.add_page()
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(190, 10, f"EMESSO DA: {studio.upper()}", ln=True)
    pdf.cell(190, 10, f"DATA: {datetime.date.today()}", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(95, 10, "INDICATORE", 1, 0, 'C')
    pdf.cell(95, 10, "VALORE", 1, 1, 'C')
    
    pdf.set_font("Arial", size=11)
    for k, v in dati.items():
        pdf.cell(95, 10, k, 1)
        pdf.cell(95, 10, str(v), 1, 1)
    
    pdf.ln(10)
    pdf.multi_cell(190, 7, "CONFORMITA: Analisi eseguita secondo standard ISA 320 e monitoraggio AI Forensic.")
    return pdf.output(dest='S').encode('latin-1')

# --- 3. INTERFACCIA E LOGICA ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM", layout="wide")

if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.title("💠 COIN-NEXUS ACCESS")
    pwd = st.text_input("PASSWORD", type="password")
    if st.button("SBLOCCA SISTEMA"):
        if pwd == "PLATINUM2026":
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

# --- DASHBOARD ---
st.title("💠 Quantum Financial Engine v3.5")
with st.sidebar:
    st.header("IMPOSTAZIONI")
    studio = st.text_input("Studio/Banca", "STUDIO_GOLD_REVISIONI")
    file = st.file_uploader("Carica Bilancio (Excel/CSV)", type=['xlsx', 'csv'])
    if st.button("CHIUDI SESSIONE"):
        st.session_state["auth"] = False
        st.rerun()

if file:
    try:
        # Caricamento e pulizia
        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        val_col = df.select_dtypes(include=[np.number]).columns[0]
        
        # Calcoli Avanzati
        ricavi = df[val_col].sum()
        mat = ricavi * 0.012
        rischio_score = 1.2 + (ricavi / 500000)
        rating = "AAA" if rischio_score > 2.5 else "BBB"
        
        # AI Detection
        iso = IsolationForest(contamination=0.05).fit(df[[val_col]])
        anomalie = len(df[iso.predict(df[[val_col]]) == -1])

        # Esposizione Dati
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("MASSA ANALIZZATA", f"€{ricavi:,.2f}")
        c2.metric("MATERIALITÀ ISA", f"€{mat:,.2f}")
        c3.metric("Z-SCORE RISCHIO", f"{rischio_score:.2f}")
        c4.metric("RATING AI", rating)

        # Grafico Quantum
        st.plotly_chart(px.area(df, y=val_col, title="Flussi Finanziari Certificati", template="plotly_dark"), use_container_width=True)

        # Report e Cloud
        st.divider()
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("💾 SINCRONIZZA CLOUD SUPABASE"):
                if client_db:
                    client_db.table("reports").insert({
                        "studio_nome": studio, "massa_totale": float(ricavi),
                        "rating": rating, "anomalie_count": int(anomalie)
                    }).execute()
                    st.success("Dati sincronizzati!")
                else:
                    st.
