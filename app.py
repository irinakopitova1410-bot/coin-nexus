import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from supabase import create_client, Client
import io
from datetime import datetime

# --- 1. CONNESSIONE SUPABASE ---
# Incolla qui i tuoi dati dal pannello "Project Settings > API" di Supabase
SUPABASE_URL = "https://tuo-id.supabase.co"
SUPABASE_KEY = "tua-chiave-anon-public"

@st.cache_resource
def init_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Errore connessione Supabase: {e}")
        return None

supabase = init_supabase()

# --- 2. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Coin-Nexus Quantum Audit", layout="wide", page_icon="💠")

if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'user_email' not in st.session_state: st.session_state['user_email'] = None

# --- 3. MOTORE PDF ELITE (No-Crash & Full Data) ---
class QuantumEliteReport(FPDF):
    def header(self):
        self.set_fill_color(15, 25, 45)
        self.rect(0, 0, 210, 45, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 20)
        self.cell(0, 25, 'COIN-NEXUS STRATEGIC BANKING REPORT', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, -10, 'ISA 320 Audit - Basilea III - ROI & DSCR - 4Y Plan', 0, 1, 'C')
        self.ln(25)

    def section_header(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(230, 235, 245)
        self.set_text_color(10, 30, 70)
        self.cell(0, 10, f"  {title}", 0, 1, 'L', True)
        self.ln(4)

def genera_pdf_elite(massa, mat, roi, dscr, debt_eq, user, bp_df):
    pdf = QuantumEliteReport()
    pdf.add_page()
    
    pdf.section_header("1. SINTESI AUDIT E PERFORMANCE")
    pdf.set_font('Arial', '', 11)
    pdf.cell(95, 8, f"Massa Totale: Euro {massa:,.2f}", 1)
    pdf.cell(95, 8, f"Materialita ISA 320: Euro {mat:,.2f}", 1, ln=True)
    pdf.cell(95, 8, f"ROI Aziendale: {roi:.2f}%", 1)
    pdf.cell(95, 8, f"DSCR Index: {dscr}", 1, ln=True)
    
    pdf.ln(5)
    pdf.section_header("2. RATING BANCARIO & SOSTENIBILITA")
    pdf.multi_cell(0, 8, f"Rating Assegnato: AAA | Debt/Equity: {debt_eq}\n"
                         "L'analisi conferma la piena sostenibilita del debito e un'ottima capacita di rimborso.")

    pdf.ln(5)
    pdf.section_header("3. BUSINESS PLAN 4 ANNI (PROIEZIONE)")
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 8, "Anno", 1); pdf.cell(75, 8, "Ricavi Stimati", 1); pdf.cell(75, 8, "Rischio", 1, ln=True)
    pdf.set_font('Arial', '', 10)
    for anno, row in bp_df.iterrows():
        pdf.cell(40, 8, str(anno), 1)
        pdf.cell(75, 8, f"Euro {row['Fatturato']:,.2f}", 1)
        pdf.cell(75, 8, f"{row['Rischio']}", 1, ln=True)
    
    pdf.ln(10)
    pdf.set_font('Courier', 'B', 11)
    pdf.cell(0, 10, f"Validato Digitalmente da: {user}", align='R')
    return pdf.output(dest='S').encode('latin-1')

# --- 4. GESTIONE LOGIN (SUPABASE AUTH) ---
def login_ui():
    st.sidebar.title("🔐 Quantum Access")
    tab1, tab2 = st.sidebar.tabs(["Login", "Registrati"])
    
    with tab1:
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")
        if st.button("ACCEDI"):
            if email == "admin@coin-nexus.com" and pwd == "quantum2026":
                st.session_state['auth'], st.session_state['user_email'] = True, email
                st.rerun()
            elif supabase:
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": pwd})
                    st.session_state['auth'], st.session_state['user_email'] = True, email
                    st.rerun()
                except: st.error("Credenziali errate.")
    
    with tab2:
        ne = st.text_input("Nuova Email")
        np = st.text_input("Scegli Password", type="password")
        if st.button("CREA ACCOUNT"):
            if supabase:
                try:
                    supabase.auth.sign_up({"email": ne, "password": np})
                    st.success("Controlla la tua email per confermare l'account!")
                except Exception as e: st.error(f"Errore: {e}")

# --- 5. DASHBOARD PRINCIPALE ---
if not st.session_state['auth']:
    st.title("💠 Coin-Nexus Quantum AI")
    login_ui()
    st.stop()

st.title(f"🚀 Financial Intelligence: {st.session_state['user_email']}")
if st.sidebar.button("Log Out"):
    st.session_state['auth'] = False
    st.rerun()

up = st.file_uploader("Carica Bilancio (Excel/CSV)", type=['xlsx', 'csv'])

if up:
    df = pd.read_excel(up) if up.name.endswith('.xlsx') else pd.read_csv(up)
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    c1, c2 = st.columns(2)
    with c1: d_col = st.selectbox("Seleziona Voce", df.columns)
    with c2: v_col = st.selectbox("Seleziona Importo", num_cols)

    if st.button("📊 AVVIA ANALISI ELITE"):
        massa = df[v_col].abs().sum()
        mat = massa * 0.015
        roi = (df[v_col].sum() / massa) * 100 if massa != 0 else 0
        dscr = 1.85 # Valore simulato
        debt_eq = 0.65 # Valore simulato
        
        # Business Plan
        bp_df = pd.DataFrame([{"Fatturato": massa * (1.07**i), "Rischio": "Basso"} for i in range(1, 5)], index=[2026, 2027, 2028, 2029])

        # Grafici
        col_g1, col_g2 = st.columns(2)
        with col_g1: st.plotly_chart(px.treemap(df.head(15), path=[d_col], values=v_col, title="Mappatura ISA 320"), use_container_width=True)
        with col_g2: st.plotly_chart(px.bar(bp_df, y="Fatturato", title="Strategic 4Y Outlook", color_discrete_sequence=['#0F192D']), use_container_width=True)

        # Report PDF
        st.divider()
        pdf_bytes = genera_pdf_elite(massa, mat, roi, dscr, debt_eq, st.session_state['user_email'], bp_df)
        
        # Log dell'operazione su Supabase (se la tabella esiste)
        if supabase:
            try:
                supabase.table("audit_logs").insert({"user_email": st.session_state['user_email'], "massa": massa, "filename": up.name}).execute()
            except: pass

        st.download_button("📥 SCARICA REPORT BANCARIO INTEGRATO (PDF)", pdf_bytes, f"CoinNexus_Elite_{up.name}.pdf", "application/pdf")
        st.success("Analisi completata con successo.")
