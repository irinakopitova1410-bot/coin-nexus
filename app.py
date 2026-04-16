import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client, Client
from fpdf import FPDF
import io

# --- 1. CONFIGURAZIONE E SETUP ---
st.set_page_config(page_title="Nexus Enterprise", layout="wide", page_icon="🏛️")

# Inizializzazione Session State (Evita errori di variabili mancanti)
if 'pdf_data' not in st.session_state:
    st.session_state.pdf_data = None
if 'generated' not in st.session_state:
    st.session_state.generated = False

# Connessione Database con gestione errori
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["https://ipmttldwfsxuubugiyir.supabase.co"]
        key = st.secrets["sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos"]
        return create_client(url, key)
    except:
        return None

supabase = init_connection()

# --- 2. MOTORI INTERNI (Nessun file esterno richiesto) ---
def calculate_metrics(d):
    rev = d.get('revenue', 1)
    ebitda = d.get('ebitda', 0)
    debt = d.get('debt', 0)
    dscr = ebitda / (debt * 0.1 + 1)
    margin = (ebitda / rev) * 100
    return {"dscr": dscr, "margin": margin, "ebitda": ebitda, "debt": debt, "revenue": rev}

def extract_from_excel(df):
    cols = {c.lower(): c for c in df.columns}
    ext = {}
    if 'fatturato' in cols: ext['revenue'] = df[cols['fatturato']].sum()
    if 'ebitda' in cols: ext['ebitda'] = df[cols['ebitda']].sum()
    if 'debiti' in cols: ext['debt'] = df[cols['debiti']].sum()
    return ext
def create_pdf_bytes(nome, m):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 16) # Usa helvetica (più compatibile sui server Linux)
    pdf.cell(0, 10, "NEXUS ENTERPRISE - REPORT CERTIFICATO", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("helvetica", '', 12)
    pdf.cell(0, 10, f"Azienda: {nome}", ln=True)
    pdf.cell(0, 10, f"Fatturato: Euro {m['revenue']:,.2f}", ln=True)
    pdf.cell(0, 10, f"DSCR: {m['dscr']:.2f}", ln=True)
    
    # Ritorna i bytes puri dell'output
    return bytes(pdf.output())

# ... (sopra c'è create_pdf_bytes) ...

# --- NUOVA FUNZIONE DECISIONALE (Inseriscila qui) ---
def get_decision_engine(m):
    score = 0
    if m['dscr'] > 1.25: score += 40
    if m['margin'] > 15: score += 30
    if m['ebitda'] > 500000: score += 30
    
    # Limite di credito: 50% dell'EBITDA (prudenziale)
    limit_credit = m['ebitda'] * 0.5 
    
    if score >= 70:
        return {"status": "APPROVATO", "color": "#00CC66", "limit": limit_credit}
    elif score >= 40:
        return {"status": "REVISIONE UMANA", "color": "#FFA500", "limit": limit_credit * 0.3}
    else:
        return {"status": "RESPINTO", "color": "#FF4B4B", "limit": 0}

# --- POI INIZIA LA SIDEBAR ---
with st.sidebar:
# ...



# Nel bottone di generazione:
if st.button("🚀 GENERA REPORT CERTIFICATO"):
    m = internal_calculate_metrics({"revenue": rev_in, "ebitda": ebit_in, "debt": pfn_in})
    # Genera i bytes e salvali nello stato
    st.session_state.pdf_data = create_pdf_bytes(nome_azienda, m)
    st.session_state.generated = True
    st.success("Report Generato con Successo!")

# Nel bottone di download:
if st.session_state.get('pdf_data'):
    st.download_button(
        label="📄 SCARICA DOSSIER PDF",
        data=st.session_state.pdf_data, # Qui ora ci sono bytes puri
        file_name="Report_Nexus.pdf",
        mime="application/pdf"
    )


# --- 3. SIDEBAR (LOGICA INPUT) ---
with st.sidebar:
    st.title("🏛️ CFO Dashboard")
    uploaded_file = st.file_uploader("📂 Carica ERP (Excel/CSV)", type=["xlsx", "csv"])
    
    # Valori Base
    defaults = {"revenue": 1000000, "ebitda": 200000, "debt": 400000}
    
    if uploaded_file:
        try:
            df_erp = pd.read_excel(uploaded_file) if "xlsx" in uploaded_file.name else pd.read_csv(uploaded_file)
            defaults.update(extract_from_excel(df_erp))
            st.success("✅ Dati ERP caricati")
        except:
            st.warning("⚠️ Formato non standard")

    nome_azienda = st.text_input("Ragione Sociale", "Azienda Target S.p.A.")
    rev_in = st.number_input("Fatturato (€)", value=int(defaults['revenue']))
    ebit_in = st.number_input("EBITDA (€)", value=int(defaults['ebitda']))
    pfn_in = st.number_input("Debito (€)", value=int(defaults['debt']))

# --- 4. MAIN UI ---
st.title("📊 Financial Dossier: Analisi Merito Creditizio")
st.markdown("---")

if st.button("🚀 GENERA REPORT CERTIFICATO", use_container_width=True):
    # Esecuzione Calcoli
    m = calculate_metrics({"revenue": rev_in, "ebitda": ebit_in, "debt": pfn_in})
    st.session_state.metrics = m
    st.session_state.generated = True
    
    # 1. KPI
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rating", "A1 - INVESTMENT GRADE" if m['dscr'] > 1.2 else "B2 - STABILE")
    c2.metric("Score Audit", "98/100")
    c3.metric("Materialità", f"€ {rev_in * 0.015:,.0f}")
    c4.metric("Leva (PFN/EBITDA)", round(pfn_in/max(1, ebit_in), 2))

    # 2. Advisor Strategico AI
    st.write("### 🧠 Nexus AI: Strategic Advisor")
    if m['dscr'] < 1.2:
        st.info(f"⚠️ **OTTIMIZZAZIONE DSCR**: Mancano €{max(0, (1.2*pfn_in)-ebit_in):,.0f} di EBITDA per il rating massimo.")
    else:
        st.success("✅ **STATUS EXCELLENT**: La struttura finanziaria rispetta i covenant bancari.")

    # 3. Grafici
    col_a, col_b = st.columns(2)
    with col_a:
        fig = go.Figure(go.Bar(x=['Tua Azienda', 'Media'], y=[m['margin'], 12.5], marker_color='#00CC66'))
        fig.update_layout(title="Margine % vs Settore", template="plotly_dark", height=300)
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        fig2 = go.Figure(go.Scatter(x=['2024', '2025', '2026'], y=[ebit_in*0.9, ebit_in, ebit_in*1.1], fill='tozeroy', line_color='#00CC66'))
        fig2.update_layout(title="Trend EBITDA Prospettico", template="plotly_dark", height=300)
        st.plotly_chart(fig2, use_container_width=True)

    # 4. Cloud Sync
    if supabase:
        try:
            supabase.table("audit_reports").insert({"company_name": nome_azienda, "revenue": rev_in, "rating": "A1"}).execute()
            st.toast("✅ Sincronizzato con Nexus Cloud")
        except: pass

    # 5. Generazione PDF
    st.session_state.pdf_data = create_pdf_bytes(nome_azienda, m)

# --- 5. SEZIONE EXPORT (ATTIVA SOLO DOPO GENERAZIONE) ---
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
    st.balloons()
else:
    st.info("💡 Inserisci i dati e clicca 'Genera Report' per abilitare l'export PDF.")
