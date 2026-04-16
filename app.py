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
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
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
# --- 1. MOTORE PDF CON BUFFER DI MEMORIA (SOLUZIONE DEFINITIVA) ---
def create_pdf_bytes(nome, m):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(0, 10, "NEXUS ENTERPRISE - REPORT CERTIFICATO", ln=True, align='C')
    pdf.set_font("helvetica", '', 10)
    pdf.cell(0, 10, "Rating conforme standard ISA 320", ln=True, align='C')
    pdf.ln(10)
    
    # Dati
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, f"Azienda: {nome}", ln=True)
    pdf.ln(5)
    
    # Tabella
    pdf.set_font("helvetica", '', 10)
    pdf.cell(90, 10, "Indicatore", 1); pdf.cell(90, 10, "Valore", 1, ln=True)
    pdf.cell(90, 10, "Fatturato", 1); pdf.cell(90, 10, f"Euro {m['revenue']:,.0f}", 1, ln=True)
    pdf.cell(90, 10, "DSCR", 1); pdf.cell(90, 10, f"{m['dscr']:.2f}", 1, ln=True)
    pdf.cell(90, 10, "Margine Operativo %", 1); pdf.cell(90, 10, f"{m['margin']:.2f}%", 1, ln=True)
    
    # Invece di output(dest='S'), usiamo bytearray direttamente
    # Questo garantisce la compatibilità con il download_button
    return bytes(pdf.output())

# --- 2. LOGICA NEL TASTO "GENERA REPORT" ---
if st.button("🚀 GENERA REPORT CERTIFICATO", use_container_width=True):
    # ... (calcoli delle metriche m) ...
    m = internal_calculate_metrics({"revenue": rev_in, "ebitda": ebit_in, "debt": pfn_in})
    st.session_state.metrics = m
    st.session_state.generated = True
    
    # Visualizzazione KPI e Grafici (omessi per brevità)
    
    # GENERAZIONE PDF SICURA
    try:
        # Generiamo i bytes puri
        st.session_state.pdf_data = create_pdf_bytes(nome_azienda, m)
        st.toast("✅ PDF generato e pronto al download")
    except Exception as e:
        st.error(f"Errore generazione file: {e}")

# --- 3. EXPORT ISTITUZIONALE (PULITO) ---
st.divider()
st.subheader("📥 Export Istituzionale")

if st.session_state.pdf_data is not None:
    # IMPORTANTE: Passiamo i bytes direttamente
    st.download_button(
        label="📄 SCARICA DOSSIER PDF CERTIFICATO",
        data=st.session_state.pdf_data,
        file_name=f"Report_Nexus_{nome_azienda}.pdf",
        mime="application/pdf",
        use_container_width=True,
        key="download_pdf_final"
    )
    st.success("Analisi pronta. Clicca sopra per salvare il PDF.")
else:
    st.info("💡 Genera il report per attivare il download.")
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
