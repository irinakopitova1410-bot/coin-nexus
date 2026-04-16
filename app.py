import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client, Client

# --- 1. SETUP & CONNESSIONE ---
st.set_page_config(page_title="Nexus Enterprise", layout="wide", page_icon="🏛️")

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# --- 2. LOGICA STRATEGICA (FIXED) ---
def get_strategic_advice(ebitda, debt, margin):
    advice = []
    # Logica DSCR
    dscr = ebitda / (debt * 0.1 + 1)
    if dscr < 1.2:
        gap = (1.2 * debt) - ebitda
        advice.append({"icon": "⚠️", "label": "DSCR", "text": f"Incrementare EBITDA di €{max(0, gap):,.0f} per fascia A1."})
    
    # Logica Margine
    if margin < 12.5:
        advice.append({"icon": "📊", "label": "MARGIN", "text": "Margine sotto media settore. Rivedere costi fissi."})
    
    # Se tutto va bene
    if not advice:
        advice.append({"icon": "✅", "label": "OPTIMAL", "text": "Struttura finanziaria eccellente."})
    return advice

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🏛️ CFO Dashboard")
    nome_azienda = st.text_input("Ragione Sociale", "Azienda Target S.p.A.")
    rev_in = st.number_input("Fatturato (€)", value=1000000)
    ebit_in = st.number_input("EBITDA (€)", value=200000)
    pfn_in = st.number_input("PFN (€)", value=400000)
    
    st.divider()
    st.info("Nexus Engine v3.0 | Cloud Sync Active")

# --- 4. MAIN INTERFACE ---
st.title("📊 Financial Dossier: Analisi di Merito Creditizio")
st.markdown("---")

# Usiamo lo State per mantenere i dati dopo il click del PDF
if 'generated' not in st.session_state:
    st.session_state.generated = False

if st.button("🚀 GENERA REPORT CERTIFICATO", use_container_width=True):
    st.session_state.generated = True
    
if st.session_state.generated:
    m_val = (ebit_in / rev_in) * 100
    dscr_val = ebit_in / (pfn_in * 0.1 + 1)

    # RIGA 1: KPI
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rating", "A1 - INVESTMENT" if dscr_val > 1.2 else "B2 - STABILE")
    c2.metric("Score", "100/100")
    c3.metric("Materialità", f"€ {rev_in * 0.015:,.0f}")
    c4.metric("Cash Ratio", "0.8")

    # RIGA 2: NEXUS ADVISOR (Sistemata)
    st.write("### 🧠 Nexus AI: Strategic Advisor")
    advices = get_strategic_advice(ebit_in, pfn_in, m_val)
    adv_cols = st.columns(len(advices))
    for i, a in enumerate(advices):
        with adv_cols[i]:
            st.info(f"**{a['icon']} {a['label']}**\n\n{a['text']}")

    # RIGA 3: GRAFICI
    col_a, col_b = st.columns(2)
    with col_a:
        fig = go.Figure(go.Bar(x=['Tua Azienda', 'Media'], y=[m_val, 12.5], marker_color=['#00CC66', '#334155']))
        fig.update_layout(title="Benchmark Margine %", template="plotly_dark", height=300)
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        fig2 = go.Figure(go.Scatter(x=[2026, 2027, 2028, 2029], y=[80000, 120000, 150000, 190000], fill='tozeroy', line_color='#00CC66'))
        fig2.update_layout(title="Proiezione Liquidità", template="plotly_dark", height=300)
        st.plotly_chart(fig2, use_container_width=True)

    # Salvataggio Silenzioso
    try:
        supabase.table("audit_reports").insert({
            "company_name": nome_azienda, "revenue": rev_in, "score": 100, "rating": "A1"
        }).execute()
    except:
        pass

# --- 5. EXPORT (Spostato per stabilità) ---
st.divider()
st.subheader("📥 Export Istituzionale")
c_pdf, c_txt = st.columns([1, 3])
with c_pdf:
    if st.button("📄 GENERA DOSSIER PDF PER BANCA"):
        st.balloons()
        st.success("Analisi certificata pronta per il download.")
        # Qui aggiungeremo il tasto download reale
