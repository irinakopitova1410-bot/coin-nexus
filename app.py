import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime

# --- CONFIGURAZIONE PRODOTTO ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM AUDIT", layout="wide")

# Styling per aumentare il valore percepito
st.markdown("""
    <style>
    .stMetric { background: #0e1117; border: 1px solid #1d4ed8; border-radius: 10px; padding: 15px; }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTORE DI ANALISI FORENSE ---
def benford_analysis(series):
    # Estrae la prima cifra
    digits = series.abs().astype(str).str.extract('([1-9])')[0].dropna().astype(int)
    observed = digits.value_counts(normalize=True).sort_index()
    expected = pd.Series({i: np.log10(1 + 1/i) for i in range(1, 10)})
    return pd.DataFrame({'Osservato': observed, 'Atteso (Benford)': expected}).fillna(0)

# --- GENERATORE REPORT COMMERCIALE ---
def genera_report_pdf(totale, mat, rischio, df_anomalie, note):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Premium
    pdf.set_fill_color(29, 78, 216)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(190, 30, "COIN-NEXUS PLATINUM AUDIT", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(25)
    
    # Sintesi Tecnica
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. SINTESI METODOLOGICA (ISA 320)", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(100, 10, f"Massa Analizzata: Euro {totale:,.2f}", 1)
    pdf.cell(90, 10, f"Soglia Materialita: Euro {mat:,.2f}", 1, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "2. NOTE DEL REVISORE", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 10, note if note else "Nessuna nota inserita.")
    
    pdf.ln(10)
    if not df_anomalie.empty:
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "3. EVIDENZE SOPRA SOGLIA", ln=True)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(140, 8, "Voce", 1)
        pdf.cell(50, 8, "Importo", 1, ln=True)
        pdf.set_font("Arial", '', 9)
        for i, row in df_anomalie.head(20).iterrows():
            txt = str(row[0]).encode('ascii', 'ignore').decode('ascii')
            pdf.cell(140, 7, txt[:60], 1)
            pdf.cell(50, 7, f"{row[1]:,.2f}", 1, ln=True)
            
    return pdf.output()

# --- INTERFACCIA COMMERCIALE ---
st.title("🛡️ Coin-Nexus Platinum: Forensic Audit")

with st.sidebar:
    st.header("⚙️ Parametri Audit")
    uploaded_file = st.file_uploader("Sincronizza Database", type=['xlsx', 'csv'])
    perc_mat = st.slider("Benchmark Materialità (%)", 0.5, 5.0, 1.5)
    note_audit = st.text_area("Note e Conclusioni per il Report")

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    col_v = df.select_dtypes(include=[np.number]).columns[0]
    col_c = df.columns[0]
    
    totale = df[col_v].sum()
    mat = totale * (perc_mat / 100)
    anomalie = df[df[col_v] > mat].sort_values(by=col_v, ascending=False)
    
    # Dashboard KPI
    c1, c2, c3 = st.columns(3)
    c1.metric("MASSA ANALIZZATA", f"€ {totale:,.2f}")
    c2.metric("SOGLIA ISA 320", f"€ {mat:,.2f}")
    c3.metric("ALERT RILEVATI", len(anomalie))

    # Analisi Benford (Il valore aggiunto)
    st.divider()
    st.subheader("🕵️ Forensic Analysis: Legge di Benford")
    benford_df = benford_analysis(df[col_v])
    st.bar_chart(benford_df)
    st.caption("Il grafico confronta la distribuzione reale delle cifre con la curva statistica attesa. Scostamenti forti indicano potenziali anomalie.")

    # Mappa Rischio
    st.plotly_chart(px.treemap(df.nlargest(20, col_v), path=[col_c], values=col_v, template="plotly_dark", title="Mappa Concentrazione Asset"), use_container_width=True)

    # Export
    st.divider()
    if st.button("🚀 GENERA REPORT PROFESSIONALE PDF"):
        pdf_out = genera_report_pdf(totale, mat, "CERTIFICATO", anomalie, note_audit)
        st.download_button("📥 SCARICA REPORT CERTIFICATO", data=bytes(pdf_out), file_name="Audit_Platinum.pdf", mime="application/pdf", use_container_width=True)

else:
    st.info("👋 Benvenuto. Carica un file per attivare l'intelligence di audit.")
