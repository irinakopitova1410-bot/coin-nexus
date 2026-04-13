import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime

# --- CONFIGURAZIONE UI ---
st.set_page_config(page_title="COIN-NEXUS QUANTUM AI", layout="wide", page_icon="💠")

st.markdown("""
    <style>
    .stApp { background: #02040a; color: #e6f1ff; }
    [data-testid="stMetricValue"] { color: #00f2ff !important; text-shadow: 0 0 10px rgba(0, 242, 255, 0.4); }
    .stMetric { background: rgba(10, 20, 40, 0.6); border: 1px solid #00f2ff; border-radius: 12px; }
    .stButton>button { 
        background: linear-gradient(45deg, #1e40af, #00f2ff); border: none; color: white; 
        font-weight: bold; border-radius: 8px; width: 100%; height: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE DI CALCOLO ---
def get_stats(df, col):
    mean, std = df[col].mean(), df[col].std()
    df['z_score'] = (df[col] - mean) / std
    outliers = df[df['z_score'].abs() > 2].copy()
    hhi = ((df[col] / df[col].sum()) ** 2).sum()
    return outliers, hhi

# --- GENERATORE PDF (MEMORY-SAFE) ---
def genera_pdf_platinum(massa, mat, anom, outliers, hhi, studio, note):
    try:
        pdf = FPDF()
        pdf.add_page()
        # Header
        pdf.set_fill_color(0, 10, 31)
        pdf.rect(0, 0, 210, 50, 'F')
        pdf.set_text_color(0, 242, 255)
        pdf.set_font("Arial", 'B', 24)
        pdf.cell(190, 30, str(studio).upper(), ln=True, align='C')
        
        pdf.set_text_color(0, 0, 0)
        pdf.ln(30)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "DATI DI REVISIONE", ln=True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(100, 10, "Massa Totale:", 1); pdf.cell(90, 10, f"{massa:,.2f}", 1, 1, 'R')
        pdf.cell(100, 10, "Materialita:", 1); pdf.cell(90, 10, f"{mat:,.2f}", 1, 1, 'R')
        pdf.cell(100, 10, "Indice HHI:", 1); pdf.cell(90, 10, f"{hhi:.4f}", 1, 1, 'R')
        
        if not anom.empty:
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "PRINCIPALI ECCEZIONI RILEVATE", ln=True)
            pdf.set_font("Arial", '', 8)
            for i in range(min(len(anom), 30)):
                row = anom.iloc[i]
                # Pulizia sicura per FPDF (solo caratteri ASCII)
                clean_desc = str(row.iloc[0]).encode('ascii', 'ignore').decode('ascii')
                pdf.cell(150, 7, clean_desc[:75], 1)
                pdf.cell(40, 7, f"{row.iloc[1]:,.2f}", 1, 1, 'R')
        
        if note:
            pdf.ln(10)
            pdf.set_font("Arial", 'I', 10)
            clean_note = str(note).encode('ascii', 'ignore').decode('ascii')
            pdf.multi_cell(0, 7, clean_note)

        # Ritorna l'output binario direttamente
        return pdf.output(dest='S')
    except Exception as e:
        return f"ERRORE_PDF: {str(e)}"

# --- INTERFACCIA ---
st.title("💠 COIN-NEXUS QUANTUM AI")

with st.sidebar:
    st.header("🏢 STUDIO SETUP")
    studio_nome = st.text_input("AUDIT FIRM ID", "PLATINUM_CORE_AI")
    uploaded = st.file_uploader("SYNC DATABASE", type=['xlsx', 'csv'])
    p_mat = st.slider("MATERIALITY %", 0.5, 5.0, 1.5)

if uploaded:
    try:
        df = pd.read_excel(uploaded) if uploaded.name.endswith('.xlsx') else pd.read_csv(uploaded)
        num_col = df.select_dtypes(include=[np.number]).columns[0]
        txt_col = df.select_dtypes(exclude=[np.number]).columns[0]
        
        massa = df[num_col].sum()
        mat_val = massa * (p_mat / 100)
        outliers, hhi_val = get_stats(df, num_col)
        anom = df[df[num_col] > mat_val].sort_values(by=num_col, ascending=False)
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("TOTAL MASS", f"€{massa:,.2f}")
        m2.metric("MATERIALITY", f"€{mat_val:,.2f}")
        m3.metric("AI OUTLIERS", len(outliers))
        m4.metric("HHI INDEX", f"{hhi_val:.3f}")

        t1, t2, t3 = st.tabs(["📊 RISK ANALYTICS", "🧠 AI INSIGHTS", "📄 MASTER REPORT"])

        with t1:
            fig = px.treemap(df.nlargest(30, num_col), path=[txt_col], values=num_col, 
                             template="plotly_dark", color_discrete_sequence=['#00f2ff'])
            st.plotly_chart(fig, use_container_width=True)
            
        with t2:
            st.subheader("🧠 Intelligence AI Summary")
            ai_text = f"Stato: {'CRITICO' if len(outliers) > 5 else 'STABILE'}. Rilevate {len(outliers)} anomalie statistiche."
            st.info(ai_text)
            st.dataframe(outliers[[txt_col, num_col, 'z_score']].head(20), use_container_width=True)

        with t3:
            st.subheader("Platinum Export System")
            note_audit = st.text_area("Audit Conclusion", value=ai_text)
            
            if st.button("🚀 ESEGUI MASTER EXPORT"):
                with st.spinner("Generazione in corso..."):
                    pdf_data = genera_pdf_platinum(massa, mat_val, anom, outliers, hhi_val, studio_nome, note_audit)
                    
                    if isinstance(pdf_data, str) and "ERRORE_PDF" in pdf_data:
                        st.error(pdf_data)
                    else:
                        # Convertiamo in bytes per sicurezza
                        final_pdf = bytes(pdf_data) if isinstance(pdf_data, (bytearray, str)) else pdf_data
                        
                        st.success("Report Generato con successo!")
                        st.download_button(
                            label="📥 SCARICA PLATINUM REPORT (PDF)",
                            data=final_pdf,
                            file_name=f"Audit_Report_{studio_nome}.pdf",
                            mime="application/pdf"
                        )
                
    except Exception as e:
        st.error(f"ENGINE_ERROR: {e}")
else:
    st.info("👋 Carica un file per attivare l'analisi Quantum.")
