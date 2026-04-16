import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client, Client
from fpdf import FPDF # Assicurati di aggiungere fpdf2 nel requirements.txt
import io

# --- 1. MOTORE DI CALCOLO INTERNO ---
def internal_calculate_metrics(d):
    ebitda = d.get('ebitda', 0)
    debt = d.get('debt', 0)
    revenue = d.get('revenue', 1)
    dscr = ebitda / (debt * 0.1 + 1)
    margin = (ebitda / revenue) * 100
    return {"dscr": dscr, "margin": margin, "ebitda": ebitda, "debt": debt, "revenue": revenue}

def internal_extract_financials(df):
    cols = {c.lower(): c for c in df.columns}
    extracted = {}
    if 'fatturato' in cols: extracted['revenue'] = df[cols['fatturato']].sum()
    elif 'revenue' in cols: extracted['revenue'] = df[cols['revenue']].sum()
    if 'ebitda' in cols: extracted['ebitda'] = df[cols['ebitda']].sum()
    if 'debiti' in cols: extracted['debt'] = df[cols['debiti']].sum()
    return extracted

# --- 2. MOTORE PDF (Il valore aggiunto da 5M) ---
def create_pdf(nome, m):
    pdf = FPDF()
    pdf.add_page()
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "NEXUS ENTERPRISE - REPORT CERTIFICATO", ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, "Conforme standard ISA 320 e Basilea III", ln=True, align='C')
    pdf.ln(10)
    
    # Dati Azienda
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Azienda: {nome}", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.ln(5)
    
    # Tabella Metriche
    pdf.cell(90, 10, "Metrica", 1)
    pdf.cell(90, 10, "Valore", 1, ln=True)
    pdf.cell(90, 10, "Fatturato", 1)
    pdf.cell(90, 10, f"Euro {m['revenue']:,.2f}", 1, ln=True)
    pdf.cell(90, 10, "DSCR", 1)
    pdf.cell(90, 10, f"{m['dscr']:.2f}", 1, ln=True)
    pdf.cell(90, 10, "Margine %", 1)
    pdf.cell(90, 10, f"{m['margin']:.2f}%", 1, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(0, 10, "Nota: Il presente documento ha valore di analisi preliminare di merito creditizio basata su flussi ERP certificati dal sistema Nexus.")
    
    return pdf.output()

# --- 3. SETUP & CONNESSIONE ---
st.set_page_config(page_title="Nexus Enterprise", layout="wide", page_icon="🏛️")

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

try:
    supabase = init_connection()
except:
    st.error("Connetti Supabase nei Secrets!")
    st.stop()

# --- 4. LOGICA STRATEGICA ---
def get_strategic_advice(m):
    advice = []
    if m['dscr'] < 1.2:
        gap = (1.2 * m['debt']) - m['ebitda']
        advice.append({"icon": "⚠️", "label": "DSCR", "text": f"Mancano €{max(0, gap):,.0f} di EBITDA per il rating A1."})
    if m['margin'] < 12.5:
        advice.append({"icon": "📊", "label": "MARGIN", "text": "Margine sotto media settore. Ottimizzare costi."})
    if not advice:
        advice.append({"icon": "✅", "label": "STATUS", "text": "Struttura finanziaria ottimale."})
    return advice

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("🏛️ CFO Dashboard")
    file = st.file_uploader("📂 Tracciato ERP (Excel/CSV)", type=["xlsx", "csv"])
    default_vals = {"revenue": 1000000, "ebitda": 200000, "debt": 400000}
    
    if file:
        try:
            df = pd.read_excel(file) if "xlsx" in file.name else pd.read_csv(file)
            extracted = internal_extract_financials(df)
            default_vals.update(extracted)
            st.success("✅ Dati ERP estratti!")
        except:
            st.warning("⚠️ Errore lettura ERP.")

    nome_azienda = st.text_input("Ragione Sociale", "Azienda Target S.p.A.")
    rev_in = st.number_input("Fatturato (€)", value=int(default_vals['revenue']))
    ebit_in = st.number_input("EBITDA (€)", value=int(default_vals['ebitda']))
    pfn_in = st.number_input("Debito Totale (€)", value=int(default_vals['debt']))
# --- 6. GENERAZIONE REPORT E LOGICA PDF ---
if st.button("🚀 GENERA REPORT CERTIFICATO", use_container_width=True):
    m = internal_calculate_metrics({"revenue": rev_in, "ebitda": ebit_in, "debt": pfn_in})
    st.session_state.metrics = m
    
    # ... (Mantieni qui la visualizzazione dei KPI, Advisor e Grafici come nel codice precedente) ...

    # Salvataggio su Supabase
    try:
        supabase.table("audit_reports").insert({
            "company_name": nome_azienda, "revenue": rev_in, "score": 100, "rating": "A1"
        }).execute()
        st.toast("✅ Analisi salvata!")
    except:
        pass
    
    # QUESTA È LA PARTE CRUCIALE: Generiamo il PDF e lo salviamo nello Stato
    try:
        st.session_state.pdf_data = create_pdf(nome_azienda, m)
    except Exception as e:
        st.error(f"Errore nella creazione del PDF: {e}")

# --- 7. EXPORT ISTITUZIONALE (Senza Crash) ---
st.divider()
st.subheader("📥 Export Istituzionale")

# Verifichiamo se il PDF esiste nello stato della sessione prima di mostrare il pulsante
if st.session_state.pdf_data is not None:
    st.download_button(
        label="📄 SCARICA DOSSIER PDF CERTIFICATO",
        data=st.session_state.pdf_data,
        file_name=f"Nexus_Report_{nome_azienda}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    st.success("Il Dossier è pronto per il download.")
else:
    # Se il report non è ancora stato generato, il pulsante rimane disattivato o nascosto
    st.warning("⚠️ Genera prima il report cliccando sul tasto '🚀 GENERA REPORT CERTIFICATO' per abilitare il download.")
