import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime
from sklearn.ensemble import IsolationForest
from supabase import create_client, Client

# --- CONFIG ---
# Assicurati che questi dati siano corretti
URL = "https://ipmttldwfsxuubugiyir.supabase.co"
KEY = "sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos" 

try:
    supabase = create_client(URL, KEY)
except:
    st.error("Errore Database")

# --- FUNZIONE PDF ---
def genera_pdf(studio, massa, rating):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "REPORT COIN-NEXUS PLATINUM", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(190, 10, f"Studio: {studio}", ln=True)
    pdf.cell(190, 10, f"Rating: {rating}", ln=True)
    pdf.cell(190, 10, f"Massa: EUR {massa:,.2f}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACCIA ---
st.set_page_config(page_title="COIN-NEXUS", layout="wide")

if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    pwd = st.text_input("LICENSE KEY", type="password")
    if st.button("LOGIN"):
        if pwd == "PLATINUM2026":
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

st.title("💠 COIN-NEXUS PLATINUM")
studio = st.sidebar.text_input("Studio", "STUDIO_REVISIONI_H")
file = st.sidebar.file_uploader("Carica Excel", type=['xlsx', 'csv'])

if file:
    df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
    col = df.select_dtypes(include=[np.number]).columns[0]
    massa = df[col].sum()
    rating = "A" if massa > 100000 else "B"

    st.metric("MASSA TOTALE", f"€{massa:,.2f}")
    st.metric("RATING", rating)

    # Azioni
    if st.button("💾 SALVA CLOUD"):
        supabase.table("reports").insert({"studio_nome": studio, "massa_totale": float(massa), "rating": rating}).execute()
        st.success("Sincronizzato!")

    pdf_bytes = genera_pdf(studio, massa, rating)
    st.download_button("📥 SCARICA REPORT PDF", data=pdf_bytes, file_name="Report.pdf")
    
    st.plotly_chart(px.histogram(df, x=col, template="plotly_dark"))
