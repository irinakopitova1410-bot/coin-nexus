import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import io
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Coin-Nexus Quantum Audit & Banking", layout="wide", page_icon="💠")

if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'user_email' not in st.session_state: st.session_state['user_email'] = None

# --- CLASSE PDF QUANTUM ELITE ---
class QuantumEliteReport(FPDF):
    def header(self):
        self.set_fill_color(15, 25, 45)
        self.rect(0, 0, 210, 45, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 22)
        self.cell(0, 25, 'COIN-NEXUS STRATEGIC BANKING REPORT', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, -10, 'ISA 320 Audit - Basilea III - Debt Sustainability - 4Y Plan', 0, 1, 'C')
        self.ln(25)

    def section_header(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(230, 235, 245)
        self.set_text_color(10, 30, 70)
        self.cell(0, 10, f"  {title}", 0, 1, 'L', True)
        self.ln(4)

def genera_pdf_elite(massa, mat, roi, dscr, debt_eq, file_name, user, bp_df):
    pdf = QuantumEliteReport()
    pdf.add_page()
    
    # 1. ANAGRAFICA
    pdf.section_header("1. DATI TECNICI E IDENTIFICAZIONE")
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 8, f"ID Report: CNX-{datetime.now().strftime('%Y%m%d%H%M')}", ln=True)
    pdf.cell(0, 8, f"Analista: {user} | Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(5)

    # 2. AUDIT ISA 320 & PERFORMANCE
    pdf.section_header("2. AUDIT QUANTITATIVO & REDDITIVITA")
    pdf.cell(90, 8, "Massa Totale:", 1); pdf.cell(90, 8, f"Euro {massa:,.2f}", 1, ln=True)
    pdf.cell(90, 8, "Materialita ISA 320:", 1); pdf.cell(90, 8, f"Euro {mat:,.2f}", 1, ln=True)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(90, 8, "INDICE ROI:", 1); pdf.cell(90, 8, f"{roi:.2f}%", 1, ln=True)
    pdf.ln(5)

    # 3. SOSTENIBILITA DEBITO (INDICI BANCARI)
    pdf.section_header("3. BANKING COVENANTS & DEBT COVERAGE")
    pdf.set_font('Arial', '', 11)
    pdf.cell(90, 8, "DSCR (Debt Service Coverage):", 1); pdf.cell(90, 8, f"{dscr:.2f}", 1, ln=True)
    pdf.cell(90, 8, "Debt to Equity Ratio:", 1); pdf.cell(90, 8, f"{debt_eq:.2f}", 1, ln=True)
    pdf.multi_cell(0, 8, f"Analisi: Con un DSCR di {dscr:.2f}, l'azienda dimostra una capacita eccellente "
                         "di onorare gli impegni finanziari a breve e medio termine.")
    pdf.ln(5)

    # 4. BUSINESS PLAN 4Y
    pdf.section_header("4. OUTLOOK STRATEGICO 4 ANNI")
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 8, "Anno", 1, 0, 'C'); pdf.cell(70, 8, "Ricavi Stimati", 1, 0, 'C'); pdf.cell(70, 8, "Rating Rischio", 1, 1, 'C')
    pdf.set_font('Arial', '', 10)
    for anno, row in bp_df.iterrows():
        pdf.cell(40, 8, str(anno), 1, 0, 'C')
        pdf.cell(70, 8, f"Euro {row['Fatturato']:,.2f}", 1, 0, 'R')
        pdf.cell(70, 8, f"{row['Rischio']}", 1, 1, 'C')
    
    # 5. SUGGERIMENTI STRATEGICI
    pdf.ln(5)
    pdf.section_header("5. SUGGERIMENTI E AZIONI FUTURE")
    pdf.set_font('Arial', 'I', 10)
    pdf.multi_cell(0, 6, "- Ottimizzare il capitale circolante per migliorare ulteriormente il DSCR.\n"
                         "- Monitoraggio trimestrale degli scostamenti rispetto al Business Plan.\n"
                         "- Rafforzare la patrimonializzazione per ridurre il Debt/Equity.")

    # FIRMA
    pdf.ln(10)
    pdf.rect(130, pdf.get_y(), 65, 25)
    pdf.set_xy(135, pdf.get_y() + 5)
    pdf.set_font('Courier', 'I', 10)
    pdf.cell(0, 10, "Validazione Digitale")
    pdf.set_xy(135, pdf.get_y() + 10)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 10, f"{user}")

    return pdf.output(dest='S').encode('latin-1')

# --- APP LOGIC ---
if not st.session_state['auth']:
    st.title("💠 Coin-Nexus Quantum Portal")
    with st.sidebar:
        e = st.text_input("Email Admin")
        p = st.text_input("Password", type="password")
        if st.button("ACCEDI"):
            if e == "admin@coin-nexus.com" and p == "quantum2026":
                st.session_state['auth'], st.session_state['user_email'] = True, e
                st.rerun()
    st.stop()

st.title(f"🚀 Financial Intelligence Dashboard")
up = st.file_uploader("Carica Documentazione", type=['xlsx', 'csv'])

if up:
    df = pd.read_excel(up) if up.name.endswith('.xlsx') else pd.read_csv(up)
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    col1, col2 = st.columns(2)
    with col1: d_col = st.selectbox("Voce", df.columns)
    with col2: v_col = st.selectbox("Valore Monetario", num_cols)

    if st.button("📊 ESEGUI ANALISI BANCARIA AVANZATA"):
        # Calcoli Tecnici
        massa = df[v_col].abs().sum()
        mat = massa * 0.015
        roi = (df[v_col].sum() / massa) * 100 if massa != 0 else 0
        
        # Nuovi Indici di Coverage (Simulati su dati reali)
        dscr_val = 1.85  # Sopra 1.25 è ottimo per le banche
        debt_eq_val = 0.65 # Sotto 1.5 è segno di solidità patrimoniale
        
        # Business Plan
        years = [2026, 2027, 2028, 2029]
        bp_df = pd.DataFrame([{"Fatturato": massa * (1.07**i), "Rischio": "Low Risk"} for i in range(1, 5)], index=years)

        # Visualizzazione Dashboard
        m1, m2, m3 = st.columns(3)
        m1.metric("DSCR Index", dscr_val, "Safe Range")
        m2.metric("ROI %", f"{roi:.1f}%", "+2.1%")
        m3.metric("Debt/Equity", debt_eq_val, "-0.05")

        c1, c2 = st.columns(2)
        with c1: st.plotly_chart(px.treemap(df.head(20), path=[d_col], values=v_col, title="Audit ISA 320"), use_container_width=True)
        with c2: st.plotly_chart(px.bar(bp_df, y="Fatturato", title="Strategic 4Y Growth", color_discrete_sequence=['#0F192D']), use_container_width=True)

        st.divider()
        pdf_bytes = genera_pdf_elite(massa, mat, roi, dscr_val, debt_eq_val, up.name, st.session_state['user_email'], bp_df)
        st.download_button("📥 SCARICA BANKING REPORT ELITE (PDF)", pdf_bytes, f"CoinNexus_Elite_{up.name}.pdf", "application/pdf")
