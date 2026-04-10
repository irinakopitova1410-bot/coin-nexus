
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM", layout="wide")

# --- FUNZIONE PDF CORRETTA (Senza .encode) ---
def genera_report_pdf(totale, mat, rischio, df_anomalie):
    pdf = FPDF()
    pdf.add_page()
    
    # Intestazione Professionale
    pdf.set_fill_color(30, 58, 138) # Blu scuro
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(190, 25, "COIN-NEXUS PLATINUM AUDIT", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(20)
    
    # Riepilogo Metrico in Tabella
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, "Parametro di Revisione", 1)
    pdf.cell(90, 10, "Valore Rilevato", 1, ln=True)
    
    pdf.set_font("Arial", '', 11)
    pdf.cell(100, 10, "Massa Monetaria Analizzata", 1)
    pdf.cell(90, 10, f"Euro {totale:,.2f}", 1, ln=True)
    pdf.cell(100, 10, "Soglia Materialita (ISA 320)", 1)
    pdf.cell(90, 10, f"Euro {mat:,.2f}", 1, ln=True)
    pdf.cell(100, 10, "Rating di Rischio Finale", 1)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(90, 10, rischio, 1, ln=True)
    
    pdf.ln(10)
    
    # SEZIONE ANOMALIE (IL VERO VALORE)
    if not df_anomalie.empty:
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(200, 0, 0)
        pdf.cell(190, 10, "DETTAGLIO VOCI SOPRA SOGLIA DI MATERIALITA", ln=True)
        pdf.set_font("Arial", '', 9)
        pdf.set_text_color(0, 0, 0)
        
        # Intestazioni tabella anomalie
        pdf.cell(140, 8, "Descrizione Voce/Conto", 1)
        pdf.cell(50, 8, "Importo", 1, ln=True)
        
        # Prime 15 anomalie per non intasare il PDF
        for i, row in df_anomalie.head(15).iterrows():
            pdf.cell(140, 7, str(row[0])[:60], 1)
            pdf.cell(50, 7, f"{row[1]:,.2f}", 1, ln=True)
            
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 5, "Dichiarazione: Il presente report e stato generato tramite algoritmi di Forensic Accounting. Le evidenze sopra riportate devono essere sottoposte a verifica documentale (Test Sostantivi).")
    
    return pdf.output()
    # Restituisce i byte direttamente (fpdf2 output() è già un bytearray/bytes)
    return pdf.output()

# --- INTERFACCIA ---
st.sidebar.title("💠 COIN-NEXUS PLATINUM")
uploaded_file = st.sidebar.file_uploader("Carica File", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        
        # Mapping Colonne
        cols = [str(c) for c in df.columns]
        col_v = next((c for c in cols if any(x in c.lower() for x in ['saldo', 'importo', 'euro', 'valore', 'amount'])), cols[0])
        col_c = next((c for c in cols if any(x in c.lower() for x in ['desc', 'voce', 'conto', 'nominativo', 'account'])), cols[1] if len(cols)>1 else cols[0])

        # Pulizia numeri
        df[col_v] = pd.to_numeric(df[col_v].astype(str).replace('[€, ]', '', regex=True), errors='coerce').fillna(0)

        st.title("🛡️ Audit Intelligence")

        totale = df[col_v].sum()
        mat = totale * 0.015
        rischio = "ALTO" if (df[col_v] > mat).any() else "CONTROLLATO"

        c1, c2, c3 = st.columns(3)
        c1.metric("TOTALE ANALIZZATO", f"€ {totale:,.2f}")
        c2.metric("SOGLIA ISA 320", f"€ {mat:,.2f}")
        c3.metric("RATING", rischio)

        # Alert
        voci_critiche = df[df[col_v] > mat]
        if not voci_critiche.empty:
            st.error(f"🚨 Rilevate {len(voci_critiche)} anomalie sopra soglia!")
            st.dataframe(voci_critiche[[col_c, col_v]])

        # Treemap
        st.plotly_chart(px.treemap(df.nlargest(20, col_v), path=[col_c], values=col_v, template="plotly_dark"), use_container_width=True)

        # REPORT PDF (Fix finale)
        st.divider()
        # --- GENERAZIONE REPORT PROFESSIONALE ---

        if st.button("🚀 GENERA REPORT AUDIT PLATINUM"):
            try:
                # Recuperiamo le voci che superano la soglia (le anomalie)
                voci_pericolose = df[df[col_v] > mat]
                
                # CHIAMATA CORRETTA: aggiungiamo 'voci_pericolose' come quarto argomento
                pdf_bytes = genera_report_pdf(totale, mat, rischio_lvl, voci_pericolose)
                
                st.download_button(
                    label="📥 SCARICA ORA IL PDF CERTIFICATO",
                    data=bytes(pdf_bytes),
                    file_name="Audit_Report_Platinum.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                st.success("Report generato con successo!")
            except Exception as e:
                st.error(f"Errore durante la creazione del PDF: {e}")
    except Exception as e:
        st.error(f"Errore tecnico: {e}")
else:
    st.info("Carica un file Excel per iniziare.")
