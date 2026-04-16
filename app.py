import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# --- 1. IMPORT PROTETTI ---
try:
    from supabase import create_client
except ImportError:
    st.error("Errore: Libreria 'supabase' non trovata nel requirements.txt")
try:
    from fpdf import FPDF
except ImportError:
    st.error("Errore: Libreria 'fpdf2' non trovata nel requirements.txt")

# --- 2. CONFIGURAZIONE ---
st.set_page_config(page_title="Nexus Enterprise", layout="wide")

# Init Session State
for key in ['pdf_data', 'generated', 'metrics']:
    if key not in st.session_state:
        st.session_state[key] = None

# Connessione Database Protetta
def get_supabase():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except:
        return None

supabase = get_supabase()

# --- 3. LOGICA CORE ---
def calculate_metrics(d):
    rev = max(d.get('revenue', 1), 1)
    ebitda = d.get('ebitda', 0)
    debt = d.get('debt', 0)
    dscr = ebitda / (debt * 0.1 + 1)
    margin = (ebitda / rev) * 100
    return {"dscr": dscr, "margin": margin, "ebitda": ebitda, "debt": debt, "revenue": rev}

def get_decision_engine(m):
    if m['dscr'] > 1.25 and m['margin'] > 10:
        return {"status": "APPROVATO", "color": "#00CC66", "limit": m['ebitda'] * 0.5}
    return {"status": "REVISIONE", "color": "#FFA500", "limit": m['ebitda'] * 0.2}

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🏛️ CFO Dashboard")
    nome_azienda = st.text_input("Azienda", "Azienda Target S.p.A.")
    rev_in = st.number_input("Fatturato (€)", value=1000000)
    ebit_in = st.number_input("EBITDA (€)", value=200000)
    pfn_in = st.number_input("Debito (€)", value=400000)

# --- 5. MAIN UI ---
st.title("📊 Financial Dossier")

if st.button("🚀 GENERA REPORT CERTIFICATO", use_container_width=True):
    m = calculate_metrics({"revenue": rev_in, "ebitda": ebit_in, "debt": pfn_in})
    st.session_state.metrics = m
    
    dec = get_decision_engine(m)
    st.session_state.generated = True

    # Display Decision
    st.subheader("💰 Decision Engine")
    st.markdown(f"<div style='background:{dec['color']};padding:20px;border-radius:10px;text-align:center;color:white;'><h2>{dec['status']}</h2></div>", unsafe_allow_html=True)
    
    # Display KPI
    c1, c2 = st.columns(2)
    c1.metric("Rating", "A1" if m['dscr'] > 1.2 else "B2")
    c2.metric("Fido Consigliato", f"€ {dec['limit']:,.0f}")

    # Generazione PDF (Byte puro per evitare AttributeError)
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", 'B', 16)
        pdf.cell(0, 10, f"REPORT: {nome_azienda}", ln=True)
        pdf.set_font("helvetica", '', 12)
        pdf.cell(0, 10, f"Fatturato: {rev_in}", ln=True)
        pdf.cell(0, 10, f"Esito: {dec['status']}", ln=True)
        st.session_state.pdf_data = bytes(pdf.output())
    except Exception as e:
        st.error(f"Errore PDF: {e}")

# --- 6. EXPORT ---
st.divider()
if st.session_state.pdf_data:
    st.download_button("📄 SCARICA PDF", st.session_state.pdf_data, "Report.pdf", "application/pdf", use_container_width=True)
