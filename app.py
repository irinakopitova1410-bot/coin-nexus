import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime
from sklearn.ensemble import IsolationForest
from supabase import create_client, Client

# --- POSIZIONE: RIGA 10-15 ---
import streamlit as st
from supabase import create_client

# Inserisci qui le credenziali che trovi su Supabase -> Project Settings -> API
URL = "https://tuo-progetto.supabase.co"
KEY = "sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos" # Usa la service role per gestire gli utenti
supabase = create_client(URL, KEY)

# --- 2. GENERATORE REPORT PDF ---
def genera_report(studio, dati, anomalie):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(0, 51, 102)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(190, 20, "COIN-NEXUS QUANTUM CERTIFICATE", ln=True, align='C')
    pdf.ln(25)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 10, f"STUDIO: {studio.upper()}", ln=True)
    pdf.cell(190, 10, f"DATA: {datetime.date.today()}", ln=True)
    pdf.ln(10)
    for k, v in dati.items():
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(90, 10, k, 1)
        pdf.set_font("Arial", size=11)
        pdf.cell(100, 10, str(v), 1, ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- 3. INTERFACCIA ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM", layout="wide")

if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.markdown("<h1 style='text-align: center;'>💠 COIN-NEXUS ACCESS</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("LICENSE KEY", type="password")
        if st.button("SBLOCCA"):
            if pwd == "PLATINUM2026":
                st.session_state["auth"] = True
                st.rerun()
    st.stop()

# --- DASHBOARD ATTIVA ---
st.title("💠 Quantum Financial Analytics")
with st.sidebar:
    st.header("CONFIG")
    studio = st.text_input("Studio Professionale", "STUDIO_GOLD_REVISIONI")
    file = st.file_uploader("Carica Bilancio (Excel/CSV)", type=['xlsx', 'csv'])

if file:
    try:
        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        
        # Cerchiamo le colonne numeriche
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            st.error("❌ Errore: Il file non contiene colonne numeriche valide. Controlla i dati!")
        else:
            # Selezioniamo la prima colonna numerica trovata
            val_col = numeric_cols[0]
            # --- PROCEDI CON I CALCOLI ---
            ricavi = df[val_col].sum()
            materialita = ricavi * 0.015
            # ... resto del codice ...
            st.success(f"Analisi completata sulla colonna: {val_col}")
    except Exception as e:
        st.error(f"Errore tecnico: {e}")
        
        # AI Detection
        model = IsolationForest(contamination=0.05).fit(df[[val_col]])
        anomalie = len(df[model.predict(df[[val_col]]) == -1])

        # Metriche
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("RICAVI TOTALI", f"€{ricavi:,.2f}")
        c2.metric("MATERIALITÀ ISA 320", f"€{materialita:,.2f}")
        c3.metric("RISCHIO REVISIONE", rischio)
        c4.metric("ANOMALIE AI", anomalie)

        st.plotly_chart(px.line(df, y=val_col, title="Andamento Flussi Certificati", template="plotly_dark"), use_container_width=True)

        # Azioni
        st.divider()
        bt1, bt2 = st.columns(2)
        with bt1:
            if st.button("💾 SALVA IN CLOUD"):
                db = get_db()
                if db:
                    db.table("reports").insert({"studio_nome": studio, "massa_totale": float(ricavi)}).execute()
                    st.success("Dati salvati su Supabase!")
                else: st.error("Chiave Database mancante.")
        with bt2:
            dati_pdf = {"Massa Totale": f"EUR {ricavi:,.2f}", "Materialita ISA": f"EUR {materialita:,.2f}", "Esito Rischio": rischio}
            pdf_bytes = genera_report(studio, dati_pdf, anomalie)
            st.download_button("📥 SCARICA PDF CERTIFICATO", data=pdf_bytes, file_name=f"Report_{studio}.pdf")

    except Exception as e:
        st.error(f"Errore caricamento: {e}")
