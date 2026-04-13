import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime
from sklearn.ensemble import IsolationForest
from supabase import create_client, Client

# --- CONFIGURAZIONE ---
SUPABASE_URL = "https://ipmttldwfsxuubugiyir.supabase.co"
SUPABASE_KEY = "METTI_QUI_LA_TUA_CHIAVE_ANON_PUBLIC" # <--- CONTROLLA QUESTA!

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except:
    st.error("Connessione Supabase fallita.")

def genera_pdf(studio, massa, rating, anomalie_count):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "COIN-NEXUS QUANTUM AI - REPORT", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(190, 10, f"Studio: {studio}", ln=True)
    pdf.cell(190, 10, f"Massa: EUR {massa:,.2f}", ln=True)
    pdf.cell(190, 10, f"Rating: {rating}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(190, 7, "Analisi conforme standard ISA 320.")
    return pdf.output(dest='S').encode('latin-1')

# --- APP INTERFACE ---
st.set_page_config(page_title="COIN-NEXUS", layout="wide")

if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    pwd = st.text_input("PASSWORD DI ACCESSO", type="password")
    if st.button("LOGIN"):
        if pwd == "PLATINUM2026":
            st.session_state["auth"] = True
            st.rerun()
        else:
            st.error("Password errata")
    st.stop()

st.title("💠 COIN-NEXUS PLATINUM")
studio = st.sidebar.text_input("Nome Studio", "STUDIO_TEST")
file = st.sidebar.file_uploader("Carica file", type=['csv', 'xlsx'])

if file:
    df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
    col = df.select_dtypes(include=[np.number]).columns[0]
    massa = df[col].sum()
    
    # AI Anomalies
    model = IsolationForest(contamination=0.05).fit(df[[col]])
    anomalie_count = len(df[model.predict(df[[col]]) == -1])
    
    rating = "Rating A" if massa > 100000 else "Rating B"

    st.metric("Massa Totale", f"€ {massa:,.2f}")
    st.metric("Rating AI", rating)

    if st.button("💾 SALVA SU CLOUD"):
        supabase.table("reports").insert({"studio_nome": studio, "massa_totale": float(massa), "rating": rating}).execute()
        st.success("Salvato!")

    pdf_bytes = genera_pdf(studio, massa, rating, anomalie_count)
    st.download_button("📥 SCARICA PDF", data=pdf_bytes, file_name="Report.pdf")
    
    st.plotly_chart(px.histogram(df, x=col, template="plotly_dark"))
