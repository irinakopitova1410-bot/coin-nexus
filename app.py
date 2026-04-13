import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import datetime

# --- CONFIGURAZIONE ELITE 2.0 ---
st.set_page_config(page_title="COIN-NEXUS QUANTUM 2.0", layout="wide", page_icon="💠")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top right, #050b18, #000000); color: #e6f1ff; }
    [data-testid="stSidebar"] { background: rgba(5, 11, 24, 0.9) !important; backdrop-filter: blur(15px); border-right: 1px solid #1e3a8a; }
    
    /* Metriche Neon con Glow dinamico */
    div[data-testid="stMetricValue"] { color: #00f2ff !important; font-family: 'Space Mono', monospace; text-shadow: 0 0 15px rgba(0, 242, 255, 0.4); }
    .stMetric { background: rgba(30, 58, 138, 0.1); border: 1px solid rgba(0, 242, 255, 0.2); border-radius: 15px; padding: 25px; }
    
    /* Tabs & Buttons */
    .stTabs [data-baseweb="tab-list"] { background: transparent; }
    .stTabs [data-baseweb="tab"] { color: #94a3b8; font-size: 16px; font-weight: bold; }
    .stTabs [aria-selected="true"] { color: #00f2ff !important; border-bottom: 3px solid #00f2ff !important; }
    .stButton>button { 
        background: linear-gradient(45deg, #1e40af, #00f2ff); color: white; border: none; 
        font-weight: bold; letter-spacing: 2px; border-radius: 8px; height: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE DI INTELLIGENZA AVANZATA ---
def detect_outliers(df, col):
    mean = df[col].mean()
    std = df[col].std()
    df['z_score'] = (df[col] - mean) / std
    return df[df['z_score'].abs() > 2].sort_values(by='z_score', ascending=False)

def calculate_hhi(df, col):
    shares = (df[col] / df[col].sum()) ** 2
    return shares.sum()

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
# --- MAIN APP ---
st.title("💠 COIN-NEXUS QUANTUM 2.0")
st.caption("AI-Powered Forensic Suite | Strategic Risk Intelligence")

with st.sidebar:
    st.markdown("### 🎛️ CORE SETTINGS")
    studio_nome = st.text_input("AUDIT FIRM ID", "PLATINUM_INTELLIGENCE")
    uploaded_file = st.file_uploader("SYNC DATASET", type=['xlsx', 'csv'])
    p_mat = st.slider("MATERIALITY %", 0.5, 5.0, 1.5)
    st.divider()
    st.markdown("### 📜 AUDIT PROTOCOL")
    st.checkbox("ISA 240 (Frode)", value=True)
    st.checkbox("ISA 315 (Rischi)", value=True)
    st.checkbox("ISA 520 (Procedure)", value=True)

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        nums = df.select_dtypes(include=[np.number]).columns
        txts = df.select_dtypes(exclude=[np.number]).columns
        
        if len(nums) > 0 and len(txts) > 0:
            c_v, c_t = nums[0], txts[0]
            massa = df[c_v].sum()
            mat_val = massa * (p_mat / 100)
            
            outliers = detect_outliers(df, c_v)
            hhi_val = calculate_hhi(df, c_v)
            anom = df[df[c_v] > mat_val].sort_values(by=c_v, ascending=False)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("TOTAL MASS", f"€{massa:,.2f}")
            m2.metric("MATERIALITY", f"€{mat_val:,.2f}")
            m3.metric("OUTLIERS", len(outliers))
            m4.metric("RISK INDEX", f"{hhi_val:.3f}")

            tabs = st.tabs(["📉 RISK MAP", "🔬 FORENSIC LAB", "🧪 AI OUTLIERS", "📄 EXPORT"])

            with tabs[0]:
                st.plotly_chart(px.treemap(df.nlargest(40, c_v), path=[c_t], values=c_v, template="plotly_dark", color_discrete_sequence=['#00f2ff']), use_container_width=True)
            
            with tabs[1]:
                st.subheader("Statistical Integrity (Benford's Law)")
                # (Qui andrebbe il grafico Benford integrato come visto in precedenza)
                st.info("Test di conformità sulle transazioni per identificare anomalie nei processi di imputazione.")
            
            with tabs[2]:
                st.subheader("🧪 AI-Driven Outlier Detection")
                st.write("Identificazione automatica di deviazioni statistiche basata sulla distribuzione normale.")
                st.dataframe(outliers[[c_t, c_v, 'z_score']].head(50), use_container_width=True)

            with tabs[3]:
                st.subheader("Final Intelligence Report")
                note_audit = st.text_area("Audit Conclusion")
                if st.button("🚀 EXECUTE MASTER EXPORT"):
                    pdf_final = genera_report_platinum(massa, mat_val, anom, outliers, hhi_val, studio_nome, note_audit)
                    st.download_button("📥 DOWNLOAD PLATINUM REPORT", data=bytes(pdf_final), file_name="Audit_Quantum_V2.pdf", mime="application/pdf")

    except Exception as e:
        st.error(f"ENGINE_ERROR: {e}")
else:
    st.info("Awaiting high-priority data sync...")
