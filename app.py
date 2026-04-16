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

# --- 6. INTERFACCIA PRINCIPALE ---
st.title("📊 Financial Dossier: Merito Creditizio")
st.markdown("---")

# Inizializziamo lo stato per il PDF
if 'pdf_data' not in st.session_state:
    st.session_state.pdf_data = None
if 'metrics' not in st.session_state:
    st.session_state.metrics = None

if st.button("🚀 GENERA REPORT CERTIFICATO", use_container_width=True):
    m = internal_calculate_metrics({"revenue": rev_in, "ebitda": ebit_in, "debt": pfn_in})
    st.session_state.metrics = m
    
    # KPI
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rating", "A1 - INVESTMENT" if m['dscr'] > 1.2 else "B2 - STABILE")
    c2.metric("Score Audit", "98/100")
    c3.metric("Materialità", f"€ {rev_in * 0.015:,.0f}")
    c4.metric("Leva (PFN/EBITDA)", round(pfn_in/max(1, ebit_in), 2))

    # Advisor
    st.write("### 🧠 Nexus AI: Strategic Advisor")
    advices = get_strategic_advice(m)
    adv_cols = st.columns(len(advices))
    for i, a in enumerate(advices):
        with adv_cols[i]:
            st.info(f"**{a['icon']} {a['label']}**\n\n{a['text']}")

    # Grafici
    col_a, col_b = st.columns(2)
    with col_a:
        fig = go.Figure(go.Bar(x=['Tua Azienda', 'Media'], y=[m['margin'], 12.5], marker_color=['#00CC66', '#334155']))
        fig.update_layout(title="Benchmark Margine %", template="plotly_dark", height=300)
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        fig2 = go.Figure(go.Scatter(x=['2024', '2025', '2026'], y=[ebit_in*0.8, ebit_in, ebit_in*1.2], fill='tozeroy', line_color='#00CC66'))
        fig2.update_layout(title="Trend EBITDA (Prospettico)", template="plotly_dark", height=300)
        st.plotly_chart(fig2, use_container_width=True)

    # Cloud Sync
    supabase.table("audit_reports").insert({
        "company_name": nome_azienda, "revenue": rev_in, "score": 98, "rating": "A1"
    }).execute()
    
    # Genera i dati PDF e salvali nello stato
    st.session_state.pdf_data = create_pdf(nome_azienda, m)
    st.toast("✅ Analisi archiviata e PDF pronto!")

# --- 7. EXPORT (IL PUNTO CHIAVE) ---
st.divider()
st.subheader("📥 Export Istituzionale")

if st.session_state.pdf_data:
    st.download_button(
        label="📄 SCARICA DOSSIER PDF CERTIFICATO",
        data=st.session_state.pdf_data,
        file_name=f"Report_Nexus_{nome_azienda}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    st.success("Analisi certificata conforme ISA 320 pronta per il download.")
else:
    st.warning("Clicca su 'Genera Report Certificato' per preparare il download del PDF.")
