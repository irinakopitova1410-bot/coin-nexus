import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime
from sklearn.ensemble import IsolationForest
import io

# --- SISTEMA DI ACCESSO (INSERIRE QUI) ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if st.session_state["authenticated"]:
        return True
    # Grafica di Login
    st.markdown("<h1 style='text-align: center; color: #00f2ff;'>💠 COIN-NEXUS ACCESS</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.write("Inserisci la chiave di licenza Platinum per accedere.")
        pwd = st.text_input("AUDIT KEY", type="password")
        if st.button("SBLOCCA SISTEMA"):
            if pwd == "PLATINUM2026": # La tua password
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Chiave non valida.")
    return False

if not check_password():
    st.stop()
# --- FINE SISTEMA DI ACCESSO ---

# Ora prosegue il tuo codice normale
st.set_page_config(page_title="COIN-NEXUS QUANTUM AI", layout="wide", page_icon="💠")
    <style>
    .stApp { background: #02040a; color: #e6f1ff; }
    [data-testid="stMetricValue"] { color: #00f2ff !important; text-shadow: 0 0 10px rgba(0, 242, 255, 0.4); }
    .stMetric { background: rgba(10, 20, 40, 0.6); border: 1px solid #00f2ff; border-radius: 12px; padding: 20px; }
    .stButton>button { 
        background: linear-gradient(45deg, #1e40af, #00f2ff); border: none; color: white; 
        font-weight: bold; border-radius: 8px; width: 100%; height: 55px; font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CORE AI ENGINE: ISOLATION FOREST ---
def detect_ai_anomalies(df, col_val):
    """Detectează anomalii folosind Machine Learning (Isolation Forest)."""
    X = df[[col_val]].values
    model = IsolationForest(contamination=0.05, random_state=42)
    df['ai_risk_score'] = model.fit_predict(X)
    # -1 înseamnă anomalie, 1 înseamnă normal
    anomalies = df[df['ai_risk_score'] == -1].copy()
    return anomalies

# --- ENGINE STATISTIC CLASIC ---
def get_classic_stats(df, col):
    mean, std = df[col].mean(), df[col].std()
    df['z_score'] = (df[col] - mean) / std
    outliers = df[df['z_score'].abs() > 2].copy()
    hhi = ((df[col] / df[col].sum()) ** 2).sum()
    return outliers, hhi

# --- GENERATOR PDF MEMORY-SAFE ---
def genera_pdf_platinum(massa, mat, anom, outliers, ai_anom, hhi, studio, note):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(0, 10, 31)
        pdf.rect(0, 0, 210, 50, 'F')
        pdf.set_text_color(0, 242, 255)
        pdf.set_font("Arial", 'B', 24)
        pdf.cell(190, 30, str(studio).upper(), ln=True, align='C')
        
        pdf.set_text_color(0, 0, 0)
        pdf.ln(30)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "RESUME EXECUTIV - AI AUDIT REPORT", ln=True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(100, 10, "Masa Totala Analizata:", 1); pdf.cell(90, 10, f"{massa:,.2f}", 1, 1, 'R')
        pdf.cell(100, 10, "Prag Materialitate (ISA 320):", 1); pdf.cell(90, 10, f"{mat:,.2f}", 1, 1, 'R')
        pdf.cell(100, 10, "Scor Concentrare Risc (HHI):", 1); pdf.cell(90, 10, f"{hhi:.4f}", 1, 1, 'R')
        pdf.cell(100, 10, "Anomalii Identificate de AI:", 1); pdf.cell(90, 10, f"{len(ai_anom)}", 1, 1, 'R')
        
        if note:
            pdf.ln(10)
            pdf.set_font("Arial", 'I', 10)
            clean_note = str(note).encode('ascii', 'ignore').decode('ascii')
            pdf.multi_cell(0, 7, f"CONCLUZII REVIZOR: {clean_note}")

        return pdf.output(dest='S')
    except Exception as e:
        return f"ERRORE_PDF: {str(e)}"

# --- INTERFAȚĂ PRINCIPALĂ ---
st.title("💠 COIN-NEXUS QUANTUM AI v2.5")
st.caption("Forensic Intelligence & Machine Learning Audit Suite")

with st.sidebar:
    st.header("⚙️ CONFIGURARE")
    studio_nome = st.text_input("AUDIT FIRM ID", "PLATINUM_AI_GLOBAL")
    uploaded = st.file_uploader("ÎNCĂRCARE BAZĂ DE DATE (XLSX, CSV)", type=['xlsx', 'csv'])
    p_mat = st.slider("MATERIALITATE %", 0.5, 5.0, 1.5)

if uploaded:
    try:
        df = pd.read_excel(uploaded) if uploaded.name.endswith('.xlsx') else pd.read_csv(uploaded)
        num_col = df.select_dtypes(include=[np.number]).columns[0]
        txt_col = df.select_dtypes(exclude=[np.number]).columns[0]
        
        # Calcul Statistici și AI
        massa = df[num_col].sum()
        mat_val = massa * (p_mat / 100)
        classic_outliers, hhi_val = get_classic_stats(df, num_col)
        ai_anomalies = detect_ai_anomalies(df, num_col)
        
        # Dashboard Metrice
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("MASĂ TOTALĂ", f"€{massa:,.2f}")
        m2.metric("MATERIALITATE", f"€{mat_val:,.2f}")
        m3.metric("ANOMALII AI", len(ai_anomalies))
        m4.metric("INDICE HHI", f"{hhi_val:.3f}")

        t1, t2, t3 = st.tabs(["📊 ANALITICĂ RISC", "🧠 INTELIGENȚĂ ARTIFICIALĂ", "📄 RAPORT FINAL"])

        with t1:
            st.plotly_chart(px.treemap(df.nlargest(30, num_col), path=[txt_col], values=num_col, 
                             template="plotly_dark", color_discrete_sequence=['#00f2ff']), use_container_width=True)
            
        with t2:
            st.subheader("🤖 Analiză de Machine Learning: Isolation Forest")
            st.write("Algoritmul a identificat tranzacții care nu respectă tiparele obișnuite ale companiei.")
            st.dataframe(ai_anomalies[[txt_col, num_col, 'ai_risk_score']].head(20), use_container_width=True)
            
        with t3:
            st.subheader("Sistem Export Platinum")
            note_audit = st.text_area("Concluzii Audit AI", value=f"Analiza a finalizat detectarea a {len(ai_anomalies)} riscuri prin Machine Learning.")
            if st.button("🚀 GENEREAZĂ RAPORT CERTIFICAT AI"):
                pdf_data = genera_pdf_platinum(massa, mat_val, classic_outliers, classic_outliers, ai_anomalies, hhi_val, studio_nome, note_audit)
                if not isinstance(pdf_data, str):
                    st.download_button("📥 DESCARCĂ RAPORTUL (PDF)", data=bytes(pdf_data), 
                                     file_name=f"Audit_Report_{studio_nome}.pdf", mime="application/pdf")
                else:
                    st.error(pdf_data)
                
    except Exception as e:
        st.error(f"ENGINE_ERROR: {e}")
else:
    st.info("👋 Încărcați un fișier pentru a activa auditul cu Inteligență Artificială.")
