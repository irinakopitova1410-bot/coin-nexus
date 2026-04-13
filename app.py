import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime
from sklearn.ensemble import IsolationForest
from supabase import create_client, Client

# --- SETUP SUPABASE ---
SUPABASE_URL = "https://ipmttldwfsxuubugiyir.supabase.co"
SUPABASE_KEY = "sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos" # <--- INCOLLA QUI IL TUO TOKEN
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- FUNZIONI INTELLIGENTI ---
def calcola_indicatori(df, val_col):
    ricavi = df[val_col].sum()
    std_dev = df[val_col].std()
    
    # Calcolo Materialità ISA 320 (0.5% - 2% dei ricavi)
    materialita = ricavi * 0.01 
    
    # Calcolo Rischio ISA (Basato sulla volatilità dei flussi)
    rischio_val = "Basso" if std_dev < (ricavi * 0.1) else "Alto"
    
    # Calcolo Rating Bancario (Score sintetico 1-100)
    score = 100 - (min((std_dev / ricavi) * 100, 50))
    rating = "A++" if score > 90 else "B" if score > 70 else "C"
    
    return ricavi, materialita, rischio_val, rating, score

def genera_pdf_avanzato(studio, dati_calc, anomalie_count):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(0, 51, 102)
    pdf.rect(0, 0, 210, 40, 'F')
    
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(190, 25, "COIN-NEXUS QUANTUM REPORT", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 10, f"STUDIO: {studio}", ln=True)
    pdf.cell(190, 10, f"DATA: {datetime.date.today()}", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(190, 10, "ANALISI QUANTITATIVA (Standard ISA 320)", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.cell(190, 8, f"- Ricavi Totali Analizzati: EUR {dati_calc[0]:,.2f}", ln=True)
    pdf.cell(190, 8, f"- Soglia di Materialita: EUR {dati_calc[1]:,.2f}", ln=True)
    pdf.cell(190, 8, f"- Grado di Rischio: {dati_calc[2]}", ln=True)
    pdf.cell(190, 8, f"- Rating Assegnato: {dati_calc[3]}", ln=True)
    pdf.cell(190, 8, f"- Anomalie Rilevate dall'AI: {anomalie_count}", ln=True)
    
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 9)
    pdf.multi_cell(190, 5, "Nota: Il presente report e stato generato tramite algoritmi di Machine Learning ed e inteso per uso professionale di revisione.")
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACCIA ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM", layout="wide")

if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.markdown("<h2 style='text-align: center;'>💠 COIN-NEXUS PLATINUM ACCESS</h2>", unsafe_allow_html=True)
    pwd = st.text_input("LICENSE KEY", type="password")
    if st.button("SBLOCCA"):
        if pwd == "PLATINUM2026":
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

# --- DASHBOARD ---
st.sidebar.title("💠 CONFIG")
studio = st.sidebar.text_input("Studio Professionale", "STUDIO_REVISIONI_GOLD")
file = st.sidebar.file_uploader("Carica Bilancio / Estratto Conto", type=['xlsx', 'csv'])

if file:
    df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
    val_col = df.select_dtypes(include=[np.number]).columns[0]
    
    # Esecuzione Calcoli
    ricavi, mat, rischio, rating, score = calcola_indicatori(df, val_col)
    
    # AI Anomalies
    model = IsolationForest(contamination=0.05).fit(df[[val_col]])
    anomalie = df[model.predict(df[[val_col]]) == -1]

    # Visualizzazione
    st.title(f"Analisi: {studio}")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("RICAVI TOTALI", f"€{ricavi:,.0f}")
    c2.metric("MATERIALITÀ (ISA)", f"€{mat:,.0f}")
    c3.metric("RATING", rating)
    c4.metric("SCORE AI", f"{score:.1f}/100")

    # Grafici
    col_left, col_right = st.columns(2)
    with col_left:
        st.plotly_chart(px.line(df, y=val_col, title="Andamento Temporale Flussi", template="plotly_dark"))
    with col_right:
        st.plotly_chart(px.box(df, y=val_col, title="Analisi Outliers (Rischi)", template="plotly_dark"))

    # Azioni Cloud & PDF
    st.divider()
    b1, b2 = st.columns(2)
    with b1:
        if st.button("💾 SINCRONIZZA CLOUD SUPABASE"):
            res = supabase.table("reports").insert({
                "studio_nome": studio,
                "massa_totale": float(ricavi),
                "rating": rating,
                "anomalie_count": int(len(anomalie))
            }).execute()
            st.success("Dati archiviati su Supabase!")
            
    with b2:
        pdf_bytes = genera_pdf_avanzato(studio, (ricavi, mat, rischio, rating), len(anomalie))
        st
