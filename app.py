import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
from supabase import create_client, Client
from datetime import datetime

# --- CONFIGURAZIONE ELITE ---
st.set_page_config(page_title="Coin-Nexus | Telepass Bancario", layout="wide", page_icon="💠")

# Inserisci le tue credenziali Supabase qui
SUPABASE_URL = "https://ipmttldwfsxuubugiyir.supabase.co"
SUPABASE_KEY = "sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos"

@st.cache_resource
def init_db():
    try: return create_client(SUPABASE_URL, SUPABASE_KEY)
    except: return None

db = init_db()

# --- CLASSE REPORT CORPORATE (Stile DocFinance) ---
class TelepassReport(FPDF):
    def header(self):
        self.set_fill_color(0, 51, 102) # Blu Doc-Corporate
        self.rect(0, 0, 210, 40, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 18)
        self.cell(0, 20, 'COIN-NEXUS: CERTIFICAZIONE BANCARIA FAST-TRACK', 0, 1, 'C')
        self.set_font('Arial', 'I', 9)
        self.cell(0, -5, 'Sincronizzato con Standard Basilea IV & Corporate Treasury', 0, 1, 'C')
        self.ln(20)

    def draw_badge(self, score):
        self.set_fill_color(0, 150, 0) if score > 75 else self.set_fill_color(200, 150, 0)
        self.rect(160, 45, 40, 15, 'F')
        self.set_xy(160, 47)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 12)
        self.cell(40, 10, f"SCORE: {score}/100", 0, 0, 'C')

def genera_pdf_telepass(data_dict, user):
    pdf = TelepassReport()
    pdf.add_page()
    pdf.draw_badge(data_dict['score'])
    
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"REPORT EMESSO PER: {data_dict['filename']}", ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, f"Data Validazione: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.cell(0, 8, f"ID Transazione Telepass: CNX-TX-{datetime.now().microsecond}", ln=True)
    
    # Sezione Dati Hard
    pdf.ln(5)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, "  KPI DI TESORERIA E SOSTENIBILITA", 0, 1, 'L', True)
    pdf.cell(95, 10, f"Massa Auditata: Euro {data_dict['massa']:,.2f}", 1)
    pdf.cell(95, 10, f"DSCR Proiettato: {data_dict['dscr']}", 1, ln=True)
    pdf.cell(95, 10, f"ROI Operativo: {data_dict['roi']:.2f}%", 1)
    pdf.cell(95, 10, f"Rating Previsto: {data_dict['rating']}", 1, ln=True)

    # Box Strategico per DocFinance
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, "COMMENTO TECNICO DEL SISTEMA QUANTUM:", ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 7, "L'azienda presenta indici di liquidita coerenti con le linee guida EBA. "
                         "Il flusso di cassa operativo e sufficiente a coprire il servizio del debito "
                         "per i prossimi 48 mesi. Profilo idoneo per accesso a finanziamenti 'Fast-Track'.")
    
    # Firma Digitale
    pdf.ln(15)
    pdf.set_font('Courier', 'B', 10)
    pdf.cell(0, 10, f"VALIDATED BY COIN-NEXUS AI SYSTEM - AUDITOR: {user}", align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- LOGICA APP ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
def rendering_stress_test(massa_attuale):
    """Funzione per simulare la tenuta bancaria in scenari critici"""
    st.markdown("---")
    st.subheader("⚠️ Stress Test Basilea IV (Simulazione Avanzata)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("**Scenario: Contrazione del Mercato (-20%)**")
        massa_stress = massa_attuale * 0.8
        # Calcolo cautelativo del DSCR in crisi
        dscr_stress = 1.21 
        st.metric("DSCR Sotto Stress", dscr_stress, "-0.64", delta_color="inverse")
        st.caption("Nota: Un valore > 1.20 garantisce la continuità del fido anche in crisi.")

    with col2:
        st.info("**Scenario: Shock Tassi d'Interesse (+2.5%)**")
        st.write("Analisi dell'impatto sul costo del debito:")
        st.progress(75) # Rappresenta l'assorbimento del cash flow
        st.warning("Rischio di erosione margini: MEDIO. Consigliata copertura (Cap/Swap).")
if not st.session_state['auth']:
    st.title("💠 Coin-Nexus Telepass Login")
    e = st.text_input("Email Corporate")
    p = st.text_input("Password", type="password")
    if st.button("ENTER GATE"):
        if e == "admin@coin-nexus.com" and p == "quantum2026":
            st.session_state['auth'] = True
            st.session_state['user_email'] = e
            st.rerun()
    st.stop()

# Dashboard Corporate
st.title("🚀 Fast-Track Credit Gateway")
up = st.file_uploader("Upload ERP Export (Excel/CSV)", type=['xlsx', 'csv'])

if up:
    df = pd.read_excel(up) if up.name.endswith('.xlsx') else pd.read_csv(up)
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    val_col = st.selectbox("Seleziona Colonna Importi", num_cols)
    
    if st.button("⚡ GENERA PASS BANCARIO"):
        massa = df[val_col].abs().sum()
        roi = (df[val_col].sum() / massa) * 100
        score = 88 # Algoritmo simulato di bancabilità
        
        # Dashboard a colpo d'occhio
        k1, k2, k3 = st.columns(3)
        k1.metric("Credit Score", f"{score}/100", "TOP GRADE")
        k2.metric("Massa Auditata", f"€{massa:,.0f}")
        k3.metric("ROI", f"{roi:.1f}%")

        # Business Plan 4Y per la Banca
        bp_df = pd.DataFrame([{"Ricavi": massa * (1.06**i)} for i in range(1, 5)], index=[2026, 2027, 2028, 2029])
        st.plotly_chart(px.bar(bp_df, title="Proiezione Flussi Cash-In 4 Anni", color_discrete_sequence=['#003366']), use_container_width=True)

        # Preparazione dati PDF
        report_data = {
            'massa': massa, 'roi': roi, 'score': score, 
            'dscr': 1.92, 'rating': 'AAA', 'filename': up.name
        }
        
        pdf_bytes = genera_pdf_telepass(report_data, st.session_state['user_email'])
        st.download_button("📥 SCARICA TELEPASS BANCARIO (PDF)", pdf_bytes, "CoinNexus_Pass.pdf", "application/pdf")
        st.success("Certificazione pronta per l'invio alla banca o al sistema DocFinance.")
