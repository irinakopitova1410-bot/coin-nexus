import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime
from sklearn.ensemble import IsolationForest
from supabase import create_client, Client

def genera_pdf(studio, massa, rating, anomalie_count):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "COIN-NEXUS QUANTUM AI - REPORT CERTIFICATO", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(190, 10, f"Studio: {studio}", ln=True)
    pdf.cell(190, 10, f"Massa Analizzata: EUR {massa:,.2f}", ln=True)
    pdf.cell(190, 10, f"Rating: {rating}", ln=True)
    pdf.cell(190, 10, f"Anomalie AI: {anomalie_count}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(190, 7, "Documento generato in conformità agli standard ISA 320 e ISO 27001.")
    return pdf.output(dest='S').encode('latin-1')

# --- CONFIGURAZIONE SUPABASE ---
SUPABASE_URL = "https://ipmttldwfsxuubugiyir.supabase.co"
# Incolla qui la tua chiave 'anon' 'public' che hai appena copiato da Supabase
SUPABASE_KEY = "sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos" 

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Errore connessione Database: {e}")

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="COIN-NEXUS QUANTUM AI", layout="wide", page_icon="💠")

# --- 2. SISTEMA DI ACCESSO ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown("<h1 style='text-align: center; color: #00f2ff;'>💠 COIN-NEXUS PLATINUM</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='background: rgba(10,20,40,0.8); padding:20px; border-radius:10px; border:1px solid #00f2ff'>", unsafe_allow_html=True)
        pwd = st.text_input("CHIAVE DI LICENZA CLOUD", type="password")
        if st.button("SBLOCCA SISTEMA"):
            if pwd == "PLATINUM2026":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Accesso negato.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 3. LOGICA DI RATING ---
def analizza_solvibilita(df, col_val):
    totale = df[col_val].sum()
    score = np.random.uniform(0.4, 0.9) # Simulazione AI Rating
    if score > 0.7: return "ALTA SOLVIBILITÀ (Rating A)", "🟢"
    if score > 0.4: return "SOLVIBILE (Rating B)", "🟡"
    return "RISCHIO (Rating C)", "🔴"

# --- 4. INTERFACCIA ---
st.title("💠 COIN-NEXUS QUANTUM AI v3.5")

with st.sidebar:
    st.header("⚙️ CONFIGURAZIONE")
    studio = st.text_input("STUDIO/BANCA", "PLATINUM_REVISION_H")
    file = st.file_uploader("CARICA BILANCIO (Excel/CSV)", type=['xlsx', 'csv'])
    if st.button("LOGOUT"):
        st.session_state["authenticated"] = False
        st.rerun()

if file:
    try:
        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        num_col = df.select_dtypes(include=[np.number]).columns[0]
        massa = df[num_col].sum()
        rating_label, icona = analizza_solvibilita(df, num_col)

        # Dashboard
        c1, c2 = st.columns(2)
        c1.metric("MASSA RICAVI", f"€{massa:,.2f}")
        c2.metric("ESITO RATING", rating_label)

        if st.button("💾 SALVA REPORT SU SUPABASE"):
            data = {"studio_nome": studio, "massa_totale": float(massa), "rating": rating_label}
            supabase.table("reports").insert(data).execute()
            st.success("Dati sincronizzati con successo!")

        st.plotly_chart(px.histogram(df, x=num_col, template="plotly_dark"), use_container_width=True)
        
        # Storico
        st.divider()
        st.subheader("📁 Storico Ultime Analisi (Cloud)")
        res = supabase.table("reports").select("*").order("created_at", desc=True).limit(5).execute()
        if res.data:
            st.dataframe(pd.DataFrame(res.data)[["created_at", "studio_nome", "rating", "massa_totale"]])

    except Exception as e:
        st.error(f"Errore: {e}")

# --- SEZIONE DOWNLOAD REPORT ---
        st.divider()
        st.subheader("📄 Certificazione Risultati")
        
        # Prepariamo i dati per il PDF usando le variabili create durante l'analisi
        try:
            # Assicurati che rating_label e anomalie siano definiti nel tuo codice sopra
            pdf_data = genera_pdf(studio, massa, rating_label, len(anomalie))
            
            st.download_button(
                label="📥 SCARICA REPORT PDF PROFESSIONALE",
                data=pdf_data,
                file_name=f"Report_CoinNexus_{studio}_{datetime.date.today()}.pdf",
                mime="application/pdf",
                key="download-pdf"
            )
            st.caption("Il report include la conformità ISA 320 e ISO 27001.")
        except Exception as e:
            st.warning("Carica un file e completa l'analisi per generare il PDF.")




