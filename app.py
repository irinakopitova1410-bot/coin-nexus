import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime

# --- CONFIGURAZIONE QUANTUM 2.1 ---
st.set_page_config(page_title="COIN-NEXUS AI", layout="wide", page_icon="💠")

# CSS Dinamico: Il bordo cambia colore se il rischio è alto!
def inject_custom_css(risk_level="normal"):
    border_color = "#00f2ff" if risk_level == "normal" else "#ff4b4b"
    glow_color = "rgba(0, 242, 255, 0.3)" if risk_level == "normal" else "rgba(255, 75, 75, 0.4)"
    
    st.markdown(f"""
        <style>
        .stApp {{ background: #02040a; color: #e6f1ff; }}
        [data-testid="stMetricValue"] {{ color: {border_color} !important; text-shadow: 0 0 10px {glow_color}; }}
        .stMetric {{ 
            background: rgba(10, 20, 40, 0.6); 
            border: 1px solid {border_color}; 
            border-radius: 12px; 
            transition: 0.5s;
        }}
        .stButton>button {{ 
            background: linear-gradient(45deg, #1e40af, {border_color}); 
            border: none; color: white; font-weight: bold; border-radius: 8px;
        }}
        </style>
        """, unsafe_allow_html=True)

# --- AI ENGINE: AUTOMATIC EXECUTIVE SUMMARY ---
def generate_ai_summary(massa, mat, outliers_count, hhi):
    status = "CRITICO" if outliers_count > 5 or hhi > 0.2 else "STABILE"
    summary = f"""
    ANALISI AUTOMATICA: Il dataset presenta uno stato di rischio {status}. 
    Con una massa di €{massa:,.2f}, abbiamo rilevato {outliers_count} anomalie statistiche (Z-Score > 2). 
    L'indice di concentrazione HHI è pari a {hhi:.4f}, indicando una {"forte dipendenza da singole voci" if hhi > 0.1 else "buona distribuzione degli asset"}.
    Si raccomanda l'ispezione immediata delle voci segnalate nel report Platinum.
    """
    return summary

# --- ENGINE CALCOLO ---
def get_stats(df, col):
    mean, std = df[col].mean(), df[col].std()
    df['z_score'] = (df[col] - mean) / std
    outliers = df[df['z_score'].abs() > 2]
    hhi = ((df[col] / df[col].sum()) ** 2).sum()
    return outliers, hhi

# --- APP LOGIC ---
inject_custom_css("normal") # Default
st.title("💠 COIN-NEXUS QUANTUM AI")

with st.sidebar:
    st.header("🏢 STUDIO SETUP")
    studio = st.text_input("AUDIT FIRM ID", "PLATINUM_CORE_AI")
    uploaded = st.file_uploader("SYNC DATABASE", type=['xlsx', 'csv'])
    p_mat = st.slider("MATERIALITY %", 0.5, 5.0, 1.5)

if uploaded:
    try:
        df = pd.read_excel(uploaded) if uploaded.name.endswith('.xlsx') else pd.read_csv(uploaded)
        num_col = df.select_dtypes(include=[np.number]).columns[0]
        txt_col = df.select_dtypes(exclude=[np.number]).columns[0]
        
        # Elaborazione
        massa = df[num_col].sum()
        mat_val = massa * (p_mat / 100)
        outliers, hhi_val = get_stats(df, num_col)
        
        # Trigger visivo di rischio
        if len(outliers) > 5: inject_custom_css("risk")
        
        # Dashboard
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("TOTAL MASS", f"€{massa:,.2f}")
        m2.metric("MATERIALITY", f"€{mat_val:,.2f}")
        m3.metric("AI OUTLIERS", len(outliers))
        m4.metric("HHI INDEX", f"{hhi_val:.3f}")
# --- GENERATORE PDF STABILIZZATO ---
def genera_pdf_platinum(massa, mat, anom, outliers, hhi, studio, note):
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Header - Usiamo Arial standard per evitare problemi di font
        pdf.set_fill_color(0, 10, 31)
        pdf.rect(0, 0, 210, 50, 'F')
        pdf.set_text_color(0, 242, 255)
        pdf.set_font("Arial", 'B', 24)
        pdf.cell(190, 30, str(studio).upper(), ln=True, align='C')
        
        pdf.set_text_color(0, 0, 0)
        pdf.ln(30)
        
        # Sintesi Parametri
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "DATI DI REVISIONE", ln=True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(100, 10, "Massa Totale:", 1); pdf.cell(90, 10, f"{massa:,.2f}", 1, 1, 'R')
        pdf.cell(100, 10, "Materialita:", 1); pdf.cell(90, 10, f"{mat:,.2f}", 1, 1, 'R')
        pdf.cell(100, 10, "Indice HHI:", 1); pdf.cell(90, 10, f"{hhi:.4f}", 1, 1, 'R')
        
        # Sezione Anomalie - Pulizia caratteri speciali
        if not anom.empty:
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "PRINCIPALI ECCEZIONI RILEVATE", ln=True)
            pdf.set_font("Arial", '', 8)
            for i in range(min(len(anom), 30)):
                row = anom.iloc[i]
                # Pulisce la descrizione da caratteri che FPDF non supporta
                clean_desc = str(row.iloc[0]).encode('ascii', 'ignore').decode('ascii')
                pdf.cell(150, 7, clean_desc[:75], 1)
                pdf.cell(40, 7, f"{row.iloc[1]:,.2f}", 1, 1, 'R')
        
        # Note Finali
        if note:
            pdf.ln(10)
            pdf.set_font("Arial", 'I', 10)
            clean_note = str(note).encode('ascii', 'ignore').decode('ascii')
            pdf.multi_cell(0, 7, clean_note)

        # Ritorna i bytes direttamente invece di salvare su disco
        return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        return f"ERRORE_PDF: {str(e)}"

# --- NEL TAB DI ESPORTAZIONE (Sostituisci il blocco del pulsante) ---
with tabs[3]:
    st.subheader("Final Intelligence Report")
    note_audit = st.text_area("Audit Conclusion", value=ai_text if 'ai_text' in locals() else "")
    
    if st.button("🚀 ESEGUI MASTER EXPORT"):
        with st.spinner("Compilazione report in corso..."):
            pdf_out = genera_pdf_platinum(massa, mat_val, anom, outliers, hhi_val, studio_nome, note_audit)
            
            if isinstance(pdf_out, str) and "ERRORE" in pdf_out:
                st.error(pdf_out)
            else:
                st.success("Report generato con successo!")
                st.download_button(
                    label="📥 SCARICA PLATINUM REPORT (PDF)",
                    data=pdf_out,
                    file_name=f"Audit_Quantum_{datetime.date.today()}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
      
