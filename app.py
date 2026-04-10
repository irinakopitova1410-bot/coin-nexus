import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="COIN-NEXUS ULTIMATE", layout="wide")

# Funzione PDF corretta per FPDF2
def genera_pdf_platinum(totale, mat, samp, rischio, anomalie, note, studio, quality_report):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(22, 27, 34)
    pdf.rect(0, 0, 210, 50, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(190, 30, studio.upper(), ln=True, align='C')
    pdf.set_text_color(0, 0, 0)
    pdf.ln(30)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "1. VERIFICA INTEGRITA DATI", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 8, "Analisi eseguita con protocollo Coin-Nexus Platinum.")
    if not anomalie.empty:
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(140, 8, "Voce", 1)
        pdf.cell(50, 8, "Importo", 1, ln=True)
        pdf.set_font("Arial", '', 8)
        for _, row in anomalie.head(20).iterrows():
            desc = str(row.iloc[0]).encode('latin-1', 'ignore').decode('latin-1')
            pdf.cell(140, 7, desc[:60], 1)
            pdf.cell(50, 7, f"{row.iloc[1]:,.2f}", 1, ln=True)
    return pdf.output()

# --- APP PRINCIPALE ---
st.title("🛡️ Coin-Nexus Ultimate Audit")

with st.sidebar:
    studio_name = st.text_input("Nome Studio", "Global Audit Firm")
    file = st.file_uploader("Carica Excel o CSV", type=['xlsx', 'csv'])
    perc_mat = st.slider("Materialità (%)", 0.5, 5.0, 1.5)

if file:
    try:
        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        nums = df.select_dtypes(include=[np.number]).columns
        chars = df.select_dtypes(include=['object']).columns
        
        if len(nums) > 0 and len(chars) > 0:
            col_v, col_c = nums[0], chars[0]
            massa = df[col_v].sum()
            mat_val = massa * (perc_mat / 100)
            anom = df[df[col_v] > mat_val].sort_values(by=col_v, ascending=False)
            
            st.metric("MASSA ANALIZZATA", f"€ {massa:,.2f}")
            
            t1, t2 = st.tabs(["📊 Analisi", "📜 Report"])
            with t1:
                st.plotly_chart(px.treemap(df.nlargest(25, col_v), path=[col_c], values=col_v, template="plotly_dark"), use_container_width=True)
            with t2:
                if st.button("🚀 GENERA PDF"):
                    pdf_final = genera_pdf_platinum(massa, mat_val, 0, "VALUTATO", anom, "", studio_name, [])
                    st.download_button("📥 Scarica", data=bytes(pdf_final), file_name="Report.pdf", mime="application/pdf")
    except Exception as e:
        st.error(f"Errore: {e}")
else:
    st.info("Carica un file per iniziare.")
