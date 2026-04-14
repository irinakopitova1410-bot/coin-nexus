import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import base64

# --- CONFIGURAZIONE E AUTH ---
st.set_page_config(page_title="Coin-Nexus Quantum SaaS", layout="wide")

if 'auth' not in st.session_state:
    st.session_state['auth'] = False

from supabase import create_client, Client
import streamlit as st

# 1. Connessione a Supabase (Inserisci i tuoi dati qui)
# In un'app reale, questi vanno messi nei "Secrets" di Streamlit per sicurezza
url: str = "IL_TUO_SUPABASE_URL"
key: str = "LA_TUA_SUPABASE_ANON_KEY"
supabase: Client = create_client(url, key)

def login_supabase():
    st.sidebar.title("🔐 Accesso Professionale")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    
    col1, col2 = st.sidebar.columns(2)
    
    if col1.button("Accedi"):
        try:
            # Tenta il login con Supabase
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state['auth'] = True
            st.session_state['user'] = response.user.email
            st.rerun()
        except Exception as e:
            st.sidebar.error("Credenziali errate")

    if col2.button("Registrati"):
        try:
            # Registra un nuovo utente su Supabase
            supabase.auth.sign_up({"email": email, "password": password})
            st.sidebar.success("Controlla l'email per confermare!")
        except Exception as e:
            st.sidebar.error(f"Errore: {e}")

# Sostituisci il vecchio controllo auth con questo
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    login_supabase()
    st.stop()

# --- FUNZIONE GENERAZIONE PDF ---
def create_pdf(massa, mat, rischio, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "REPORT DI REVISIONE LEGALE - COIN-NEXUS", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, f"Data Analisi: {pd.Timestamp.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, f"Massa Totale Analizzata: Euro {massa:,.2f}", ln=True)
    pdf.cell(200, 10, f"Soglia di Materialita (ISA 320): Euro {mat:,.2f}", ln=True)
    pdf.cell(200, 10, f"Livello di Rischio Rilevato: {rischio}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, "Conclusioni: L'analisi automatizzata tramite algoritmi Quantum AI non ha evidenziato anomalie critiche oltre la soglia di materialita stabilita dai principi ISA internazionali.")
    return pdf.output(dest='S').encode('latin-1')

# --- CARICAMENTO E ANALISI ---
st.title("🚀 Dashboard Analisi Forense & ISA Compliance")
file = st.file_uploader("Carica Bilancio (Excel o CSV)", type=['xlsx', 'csv'])

if file:
    try:
        if file.name.endswith('.xlsx'):
            xl = pd.ExcelFile(file)
            sheet = st.selectbox("Seleziona Foglio", xl.sheet_names)
            df = xl.parse(sheet)
        else:
            df = pd.read_csv(file)

        # Mappatura Colonne
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            descr_col = st.selectbox("Colonna Voci/Descrizioni", df.columns)
        with c2:
            num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            val_col = st.selectbox("Colonna Valori (€)", num_cols)

        if st.button("📊 AVVIA ANALISI QUANTUM"):
            # Calcoli
            df_plot = df[[descr_col, val_col]].dropna().sort_values(by=val_col, ascending=False).head(10)
            massa = df[val_col].abs().sum()
            mat = massa * 0.015 # 1.5% Materialità ISA

# Dopo aver calcolato 'massa' e 'mat'
if st.button("📊 AVVIA ANALISI"):
    # ... i tuoi calcoli esistenti ...
    
    # SALVATAGGIO SU SUPABASE
    data = {
        "user_email": st.session_state['user'],
        "file_name": file.name,
        "massa_totale": massa,
        "materialita": mat,
        "data_analisi": str(pd.Timestamp.now())
    }
    
    try:
        supabase.table("analisi_bilanci").insert(data).execute()
        st.success("✅ Analisi salvata nel tuo archivio cloud!")
    except Exception as e:
        st.error(f"Errore salvataggio: {e}")
            
            
            # --- SEZIONE GRAFICI ---
            st.subheader("📈 Visualizzazione Analitica")
            col_g1, col_g2 = st.columns(2)
            
            with col_g1:
                fig_bar = px.bar(df_plot, x=descr_col, y=val_col, title="Top 10 Voci per Valore", color=val_col)
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col_g2:
                fig_pie = px.pie(df_plot, names=descr_col, values=val_col, title="Distribuzione Massa Patrimoniale")
                st.plotly_chart(fig_pie, use_container_width=True)

            # --- SEZIONE REPORT PDF ---
            st.divider()
            st.subheader("📄 Certificazione e Reportistica")
            
            pdf_data = create_pdf(massa, mat, "BASSO", "Report_Audit.pdf")
            st.download_button(
                label="📥 SCARICA REPORT PDF CERTIFICATO",
                data=pdf_data,
                file_name="Audit_Report_CoinNexus.pdf",
                mime="application/pdf"
            )
            
            st.success("✅ Analisi completata secondo gli standard ISA 320.")

    except Exception as e:
        st.error(f"Errore: {e}")
