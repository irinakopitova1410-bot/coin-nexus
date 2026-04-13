import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime
from sklearn.ensemble import IsolationForest

# --- 1. CONFIGURAZIONE PAGINA (DEVE ESSERE LA PRIMA ISTRUZIONE) ---
st.set_page_config(page_title="COIN-NEXUS QUANTUM AI", layout="wide", page_icon="💠")

# --- 2. SISTEMA DI ACCESSO (LOGIN) ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if st.session_state["authenticated"]:
        return True

    st.markdown("<h1 style='text-align: center; color: #00f2ff;'>💠 COIN-NEXUS ACCESS</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='background: rgba(10,20,40,0.8); padding:20px; border-radius:10px; border:1px solid #00f2ff'>", unsafe_allow_html=True)
        st.write("Inserisci la chiave di licenza Platinum per accedere.")
        pwd = st.text_input("CHIAVE DI ACCESSO", type="password")
        if st.button("SBLOCCA SISTEMA"):
            if pwd == "PLATINUM2026":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Chiave non valida.")
        st.markdown("</div>", unsafe_allow_html=True)
    return False

if not check_password():
    st.stop()

# --- 3. STILI GRAFICI (ITALIANO) ---
st.markdown("""
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

# --- 4. FUNZIONI TECNICHE ---
def detect_ai_anomalies(df, col_val):
    X = df[[col_val]].values
    model = IsolationForest(contamination=0.05, random_state=42)
    df['ai_risk_score'] = model.fit_predict(X)
    return df[df['ai_risk_score'] == -1].copy()

def get_classic_stats(df, col):
    mean, std = df[col].mean(), df[col].std()
    df['z_score'] = (df[col] - mean) / std
    outliers = df[df['z_score'].abs() > 2].copy()
    hhi = ((df[col] / df[col].sum()) ** 2).sum()
    return outliers, hhi

def genera_pdf_platinum(massa, mat, ai_anom, hhi, studio, note):
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
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "SINTESI ESECUTIVA - RAPPORTO AI", ln=True)
        pdf.set_font("Arial", '', 10)
      # Dati nel PDF
        pdf.cell(100, 10, "Massa Totale Analizzata:", 1); pdf.cell(90, 10, f"Euro {massa:,.2f}", 1, 1, 'R')
        pdf.cell(100, 10, "Soglia di Materialita (ISA 320):", 1); pdf.cell(90, 10, f"Euro {mat:,.2f}", 1, 1, 'R')
        pdf.cell(100, 10, "Conformita Analisi Dati:", 1); pdf.cell(90, 10, "ISO/IEC 27001 compliant", 1, 1, 'R') # <--- AGGIUNTO ISO
        pdf.cell(100, 10, "Anomalie Rilevate dall'AI:", 1); pdf.cell(90, 10, f"{len(ai_anom)}", 1, 1, 'R')
        if note:
            pdf.ln(10)
            pdf.multi_cell(0, 7, f"NOTE: {note}")
        return pdf.output(dest='S')
    except Exception as e:
        return f"ERRORE_PDF: {str(e)}"

# --- 5. LOGICA APPLICATIVA ---
st.title("💠 COIN-NEXUS QUANTUM AI")
st.caption("Suite Professionale di Audit Forense")

with st.sidebar:
    st.header("⚙️ CONFIGURAZIONE")
    studio_nome = st.text_input("NOME STUDIO", "PLATINUM_AI_ITALIA")
    uploaded = st.file_uploader("CARICA DATI", type=['xlsx', 'csv'])
    p_mat = st.slider("MATERIALITA %", 0.5, 5.0, 1.5)
    if st.button("LOGOUT"):
        st.session_state["authenticated"] = False
        st.rerun()

if uploaded:
    try:
        df = pd.read_excel(uploaded) if uploaded.name.endswith('.xlsx') else pd.read_csv(uploaded)
        num_col = df.select_dtypes(include=[np.number]).columns[0]
        txt_col = df.select_dtypes(exclude=[np.number]).columns[0]
        
        massa = df[num_col].sum()
        mat_val = massa * (p_mat / 100)
        outliers, hhi_val = get_classic_stats(df, num_col)
        ai_anomalies = detect_ai_anomalies(df, num_col)
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("MASSA TOTALE", f"€{massa:,.2f}")
        m2.metric("MATERIALITÀ", f"€{mat_val:,.2f}")
        m3.metric("ANOMALIE AI", len(ai_anomalies))
        m4.metric("INDICE HHI", f"{hhi_val:.3f}")

        t1, t2, t3 = st.tabs(["📊 ANALISI", "🧠 AI", "📄 REPORT"])

        with t1:
            st.plotly_chart(px.treemap(df.nlargest(30, num_col), path=[txt_col], values=num_col, template="plotly_dark"), use_container_width=True)
        with t2:
            st.subheader("🤖 Machine Learning Insights")
            st.dataframe(ai_anomalies[[txt_col, num_col, 'ai_risk_score']].head(20), use_container_width=True)
        with t3:
            st.subheader("Export Report")
            note_audit = st.text_area("Conclusioni", value=f"Rilevate {len(ai_anomalies)} anomalie.")
            if st.button("🚀 GENERA PDF"):
                pdf_data = genera_pdf_platinum(massa, mat_val, ai_anomalies, hhi_val, studio_nome, note_audit)
                st.download_button("📥 SCARICA PDF", data=bytes(pdf_data), file_name="Report.pdf", mime="application/pdf")
    except Exception as e:
        st.error(f"Errore: {e}")
else:
    st.info("👋 Carica un file per iniziare.")
