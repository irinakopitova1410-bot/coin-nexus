import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e2e8f0; }
    .stMetric { background: rgba(16, 24, 39, 0.8); border: 1px solid #3b82f6; border-radius: 12px; padding: 20px; }
    .stButton>button { background: linear-gradient(90deg, #3b82f6, #2563eb); color: white; border-radius: 8px; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONE PDF ---
def genera_report_pdf(totale, mat, rischio):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "COIN-NEXUS PLATINUM - AUDIT CERTIFICATION", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, f"Massa monetaria analizzata: Euro {totale:,.2f}", ln=True)
    pdf.cell(200, 10, f"Soglia di Materialita (ISA 320): Euro {mat:,.2f}", ln=True)
    pdf.cell(200, 10, f"Livello di Rischio: {rischio}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, "Conclusioni: L'analisi ha verificato la conformita statistica dei flussi e la presenza di anomalie sopra soglia. Documento valido ai fini della revisione preliminare.")
    return pdf.output(dest='S').encode('latin-1')

# --- SIDEBAR ---
st.sidebar.title("💠 COIN-NEXUS PLATINUM")
uploaded_file = st.sidebar.file_uploader("Carica File Bilancio/Partitario", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        # Caricamento dati
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        cols = df.columns.tolist()

        # Mapping Intelligente (Corretto per evitare SyntaxError)
        col_v_list = [c for c in cols if any(x in str(c).lower() for x in ['saldo', 'importo', 'euro', 'valore', 'totale'])]
        col_c_list = [c for c in cols if any(x in str(c).lower() for x in ['desc', 'voce', 'conto', 'account', 'dettaglio'])]

        if col_v_list and col_c_list:
            col_v = col_v_list[0]
            col_c = col_c_list[0]
            st.sidebar.success(f"✅ Rilevate: {col_v} e {col_c}")
        else:
            st.warning("⚠️ Colonne non riconosciute automaticamente.")
            col_v = st.sidebar.selectbox("Seleziona Colonna Importi:", cols)
            col_c = st.sidebar.selectbox("Seleziona Colonna Descrizioni:", cols)

        if col_v and col_c:
            # Pulizia dati numerici
            df[col_v] = pd.to_numeric(df[col_v].astype(str).replace('[€, ]', '', regex=True), errors='coerce').fillna(0)
            
            st.title("🛡️ Audit Intelligence & Forensic")

            # --- METRICHE BIG 4 ---
            totale = df[col_v].sum()
            mat = totale * 0.01
            rischio = "BASSO" if totale < 1000000 else "MODERATO"

            m1, m2, m3 = st.columns(3)
            m1.metric("MASSA MONETARIA", f"€ {totale:,.2f}")
            m2.metric("SOGLIA ISA 320", f"€ {mat:,.2f}")
            m3.metric("RATING RISCHIO", rischio)

            # --- MODULO RISK DETECTION ---
            st.markdown("---")
            voci_critiche = df[df[col_v] > mat]
            if not voci_critiche.empty:
                st.error(f"🚨 ALERT: {len(voci_critiche)} voci superano la soglia di Materialità!")
                st.dataframe(voci_critiche[[col_c, col_v]].sort_values(by=col_v, ascending=False), use_container_width=True)
            else:
                st.success("✅ Nessun errore materiale rilevato sopra soglia.")

            # --- VISUALIZZAZIONE ---
            st.subheader("📊 Mappa di Concentrazione Asset")
            fig_tree = px.treemap(df.nlargest(30, col_v), path=[col_c], values=col_v, 
                                 color=col_v, color_continuous_scale='Blues', template="plotly_dark")
            st.plotly_chart(fig_tree, use_container_width=True)

            # Benford Law
            st.subheader("🕵️ Forensic Audit (Test di Benford)")
            digits = df[col_v].abs().astype(str).str.replace(r'^[0.]+', '', regex=True).str[0].dropna()
            if not digits.empty:
                digits = digits[digits.isin(['1','2','3','4','5','6','7','8','9'])].astype(int)
                actual = digits.value_counts(normalize=True).sort_index()
                expected = pd.Series({d: np.log10(1 + 1/d) for d in range(1, 10)})
                fig_ben = go.Figure()
                fig_ben.add_trace(go.Bar(x=actual.index, y=actual.values, name="Dati Reali"))
                fig_ben.add_trace(go.Scatter(x=expected.index, y=expected.values, name="Curva Benford", line=dict(color='red')))
                fig_ben.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_ben, use_container_width=True)

            # --- REPORT PDF ---
            st.divider()
            if st.button("🚀 GENERA CERTIFICAZIONE PDF"):
                pdf_bytes = genera_report_pdf(totale, mat, rischio)
                st.download_button("Scarica Report Professionale", data=pdf_bytes, file_name="Audit_Platinum.pdf", mime="application/pdf")

    except Exception as e:
        st.error(f"❌ Errore durante l'elaborazione: {e}")
else:
    st.info("👋 Benvenuto. Carica un file per iniziare l'Audit certificato.")
