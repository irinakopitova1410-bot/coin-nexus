import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime

# --- CONFIGURAZIONE ENTERPRISE ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM AUDIT", layout="wide", page_icon="🛡️")

# CSS per Design scuro e professionale
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 15px; }
    div[data-testid="stExpander"] { border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONI TECNICHE ---
def benford_check(data):
    """Analisi statistica delle prime cifre (Forensic Audit)"""
    digits = data.abs().astype(str).str.extract('([1-9])')[0].dropna().astype(int)
    if digits.empty: return pd.DataFrame()
    obs = digits.value_counts(normalize=True).sort_index()
    exp = pd.Series({i: np.log10(1 + 1/i) for i in range(1, 10)})
    return pd.DataFrame({'Reale': obs, 'Atteso': exp}).fillna(0)

def genera_pdf_enterprise(totale, mat, samp, rischio, anomalie, note):
    pdf = FPDF()
    pdf.add_page()
    
    # Intestazione istituzionale
    pdf.set_fill_color(13, 17, 23)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(190, 30, "COIN-NEXUS PLATINUM AUDIT", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(25)
    
    # Parametri di Revisione
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. PARAMETRI DI PIANIFICAZIONE (ISA 320)", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(100, 10, f"Massa Analizzata: Euro {totale:,.2f}", 1)
    pdf.cell(90, 10, f"Materialita (PM): Euro {mat:,.2f}", 1, ln=True)
    pdf.cell(100, 10, f"Soglia Errore (SAMP): Euro {samp:,.2f}", 1)
    pdf.cell(90, 10, f"Rating Rischio: {rischio}", 1, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "2. CONCLUSIONI DEL REVISORE", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 8, note if note else "Non sono state inserite note manuali al report.")
    
    # Tabella Eccezioni (Correzione KeyError)
    if not anomalie.empty:
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "3. DETTAGLIO ECCEZIONI RILEVATE", ln=True)
        pdf.set_font("Arial", 'B', 10)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(140, 8, "Voce di Bilancio", 1, 0, 'C', True)
        pdf.cell(50, 8, "Importo", 1, 1, 'C', True)
        
        pdf.set_font("Arial", '', 9)
        for _, row in anomalie.head(30).iterrows():
            # Selezione sicura delle colonne per posizione invece che per nome
            desc = str(row.iloc[0]).encode('ascii', 'ignore').decode('ascii')
            val = row.iloc[1]
            pdf.cell(140, 7, desc[:65], 1)
            pdf.cell(50, 7, f"{val:,.2f}", 1, 1, 'R')
            
    return pdf.output()

# --- INTERFACCIA ---
st.title("🛡️ Coin-Nexus Audit Platinum")
st.caption("Intelligence Forense conforme ai principi ISA 320")

with st.sidebar:
    st.header("📋 Input Dati")
    file = st.file_uploader("Carica Bilancio/Giornale", type=['xlsx', 'csv'])
    st.divider()
    st.header("⚙️ Metodologia Audit")
    perc_mat = st.slider("Materialità (% del Totale)", 0.5, 3.0, 1.5, help="Di solito tra 1% e 2%")
    perc_samp = st.slider("SAMP (% della Materialità)", 1, 10, 5, help="Soglia errore trascurabile")
    user_notes = st.text_area("Note e conclusioni professionali", placeholder="Inserisci qui il tuo giudizio...")

if file:
    try:
        # Caricamento
        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        
        # Pulizia dati: isola colonne numeriche e descrittive
        nums = df.select_dtypes(include=[np.number]).columns
        chars = df.select_dtypes(include=['object']).columns
        
        if len(nums) == 0 or len(chars) == 0:
            st.error("Il file deve contenere almeno una colonna di testo e una numerica.")
        else:
            col_v = nums[0]
            col_c = chars[0]
            
            # Calcoli Core
            massa = df[col_v].sum()
            mat_val = massa * (perc_mat / 100)
            samp_val = mat_val * (perc_samp / 100)
            anom = df[df[col_v] > mat_val].sort_values(by=col_v, ascending=False)
            
            # KPI
            c1, c2, c3 = st.columns(3)
            c1.metric("MASSA ANALIZZATA", f"€ {massa:,.2f}")
            c2.metric("MATERIALITÀ (PM)", f"€ {mat_val:,.2f}")
            c3.metric("SAMP (ERRORE)", f"€ {samp_val:,.2f}")
            
            # Tab Expander per i dettagli
            with st.expander("📊 Visualizzazione Distribuzione Asset", expanded=True):
                fig = px.treemap(df.nlargest(25, col_v), path=[col_c], values=col_v, 
                                 template="plotly_dark", color=col_v, color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True)
            
            # Sezione Forensic
            st.subheader("🕵️ Analisi Forense (Legge di Benford)")
            ben_df = benford_check(df[col_v])
            if not ben_df.empty:
                st.bar_chart(ben_df)
                st.caption("Scostamenti significativi tra 'Reale' e 'Atteso' suggeriscono potenziali manipolazioni dei dati.")
            
            # Export
            st.divider()
            if st.button("🚀 GENERA REPORT CERTIFICATO (PDF)", use_container_width=True):
                with st.spinner("Generazione certificazione in corso..."):
                    pdf_data = genera_pdf_enterprise(massa, mat_val, samp_val, "VALUTATO", anom, user_notes)
                    st.download_button(
                        "📥 SCARICA PDF FIRMATO",
                        data=bytes(pdf_data),
                        file_name=f"Audit_Report_{datetime.date.today()}.pdf",
                        mime="application/pdf"
                    )
    except Exception as e:
        st.error(f"Si è verificato un errore nel processare il file. Assicurati che il formato sia corretto.")
else:
    st.info("👋 Inizia caricando un file Excel o CSV per attivare l'analisi dei rischi.")
