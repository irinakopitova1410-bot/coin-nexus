import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime

# --- CONFIGURAZIONE ESTETICA (Valore Percepito) ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM AUDIT", layout="wide")

st.markdown("""
    <style>
    .stMetric { background: rgba(16, 24, 39, 0.8); border: 1px solid #3b82f6; border-radius: 12px; padding: 15px; }
    .stButton>button { background: #2563eb; color: white; border-radius: 8px; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTORE PDF (Progettato per non crashare) ---
def genera_report_pdf(totale, mat, rischio, df_anomalie):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Istituzionale Blu
    pdf.set_fill_color(30, 58, 138)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(190, 25, "COIN-NEXUS PLATINUM AUDIT", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(30)
    
    # Sezione Metriche
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, "Parametro di Revisione", 1)
    pdf.cell(90, 10, "Valore", 1, ln=True)
    
    pdf.set_font("Arial", '', 11)
    pdf.cell(100, 10, "Totale Masse Analizzate", 1)
    pdf.cell(90, 10, f"Euro {totale:,.2f}", 1, ln=True)
    pdf.cell(100, 10, "Soglia Materialita (ISA 320)", 1)
    pdf.cell(90, 10, f"Euro {mat:,.2f}", 1, ln=True)
    pdf.cell(100, 10, "Livello di Rischio", 1)
    pdf.cell(90, 10, str(rischio), 1, ln=True)
    
    pdf.ln(10)
    
    # Tabella Anomalie (Il valore tecnico)
    if not df_anomalie.empty:
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(200, 0, 0)
        pdf.cell(190, 10, "ANOMALIE SOPRA SOGLIA DI MATERIALITA", ln=True)
        pdf.ln(5)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(140, 8, "Voce di Bilancio", 1)
        pdf.cell(50, 8, "Importo (Euro)", 1, ln=True)
        
        pdf.set_font("Arial", '', 9)
        for i, row in df_anomalie.head(25).iterrows():
            # Pulizia per caratteri speciali (Evita l'errore '0')
            desc = str(row[0]).encode('latin-1', 'ignore').decode('latin-1')
            pdf.cell(140, 7, desc[:65], 1)
            pdf.cell(50, 7, f"{row[1]:,.2f}", 1, ln=True)
            
    return pdf.output()

# --- INTERFACCIA APP ---
st.title("🛡️ Audit Intelligence & Forensic Platform")

uploaded_file = st.sidebar.file_uploader("Sincronizza File Excel/CSV", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        # Caricamento intelligente
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        
        # Identificazione Colonne
        col_v = df.select_dtypes(include=[np.number]).columns[0]
        col_c = df.columns[0]
        
        # Calcoli di Valore (Audit Reale)
        totale = df[col_v].sum()
        mat = totale * 0.015
        anomalie = df[df[col_v] > mat].sort_values(by=col_v, ascending=False)
        rischio_final = "ALTO" if len(anomalie) > 0 else "BASSO"

        # Dashboard Metriche
        c1, c2, c3 = st.columns(3)
        c1.metric("MASSA MONETARIA", f"€ {totale:,.2f}")
        c2.metric("SOGLIA ISA 320", f"€ {mat:,.2f}")
        c3.metric("RISCHIO AUDIT", rischio_final)

        # Treemap Professionale
        st.subheader("📊 Distribuzione Asset e Concentrazione Rischio")
        fig = px.treemap(df.nlargest(20, col_v), path=[col_c], values=col_v, template="plotly_dark", color=col_v, color_continuous_scale='RdBu')
        st.plotly_chart(fig, use_container_width=True)

        # SEZIONE EXPORT (Il valore +200%)
        st.divider()
        st.subheader("📥 Certificazione Reportistica")
        
        if st.button("🚀 GENERA REPORT TECNICO PLATINUM"):
            try:
                pdf_output = genera_report_pdf(totale, mat, rischio_final, anomalie)
                st.download_button(
                    label="📥 SCARICA ORA IL PDF CERTIFICATO",
                    data=bytes(pdf_output),
                    file_name=f"Audit_Report_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                st.success("Analisi completata. Report pronto per la firma.")
            except Exception as e_pdf:
                st.error(f"Errore critico PDF: {e_pdf}")

    except Exception as e:
        st.error(f"Errore nel processare il file: {e}")
else:
    st.info("👋 In attesa di database per l'elaborazione dei rischi.")
