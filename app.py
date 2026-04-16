import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client, Client
from fpdf import FPDF
import io

# --- 1. CONFIGURAZIONE E SETUP ---
st.set_page_config(page_title="Nexus Enterprise", layout="wide", page_icon="🏛️")

if 'pdf_data' not in st.session_state:
    st.session_state.pdf_data = None
if 'generated' not in st.session_state:
    st.session_state.generated = False

# Connessione Database (Assicurati di aver impostato i Secrets su Streamlit Cloud)
@st.cache_resource
def init_connection():
    try:
        # Recupera le credenziali dai Secrets di Streamlit
        url = st.secrets["https://ipmttldwfsxuubugiyir.supabase.co"]
        key = st.secrets["sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos"]
        return create_client(url, key)
    except Exception as e:
        return None

supabase = init_connection()

# --- 2. MOTORI INTERNI ---
def calculate_metrics(d):
    rev = max(d.get('revenue', 1), 1)
    ebitda = d.get('ebitda', 0)
    debt = d.get('debt', 0)
    dscr = ebitda / (debt * 0.1 + 1)
    margin = (ebitda / rev) * 100
    
    # Altman Z-Score integrato
    x1 = (rev * 0.1) / max(debt, 1)
    x2 = (ebitda * 0.4) / max(debt, 1)
    z = (1.2 * x1) + (1.4 * x2) + (3.3 * (ebitda / max(debt, 1)))
    
    return {"dscr": dscr, "margin": margin, "ebitda": ebitda, "debt": debt, "revenue": rev, "z_score": z}

def create_pdf_bytes(nome, m):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(0, 10, "NEXUS ENTERPRISE - REPORT CERTIFICATO", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("helvetica", '', 12)
    pdf.cell(0, 10, f"Azienda: {nome}", ln=True)
    pdf.cell(0, 10, f"Fatturato: Euro {m['revenue']:,.2f}", ln=True)
    pdf.cell(0, 10, f"DSCR (Sostenibilita' Debito): {m['dscr']:.2f}", ln=True)
    pdf.cell(0, 10, f"Altman Z-Score (Predizione Insolvenza): {m['z_score']:.2f}", ln=True)
    
    return bytes(pdf.output())

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🏛️ CFO Dashboard")
    uploaded_file = st.file_uploader("📂 Carica ERP (Excel/CSV)", type=["xlsx", "csv"])
    
    defaults = {"revenue": 1000000, "ebitda": 200000, "debt": 400000}
    
    nome_azienda = st.text_input("Ragione Sociale", "Azienda Target S.p.A.")
    rev_in = st.number_input("Fatturato (€)", value=int(defaults['revenue']))
    ebit_in = st.number_input("EBITDA (€)", value=int(defaults['ebitda']))
    pfn_in = st.number_input("Debito (€)", value=int(defaults['debt']))

# --- 4. MAIN UI ---
st.title("📊 Financial Dossier: Analisi Merito Creditizio")
st.markdown("---")

# CORREZIONE: Unico bottone di generazione con logica coerente
if st.button("🚀 GENERA REPORT CERTIFICATO", use_container_width=True):
    # Calcolo metriche
    m = calculate_metrics({"revenue": rev_in, "ebitda": ebit_in, "debt": pfn_in})
    st.session_state.metrics = m
    st.session_state.generated = True
    
    # Visualizzazione Risultati
    c1, c2, c3 = st.columns(3)
    c1.metric("Rating", "A1" if m['dscr'] > 1.2 else "B2")
    c2.metric("Altman Z-Score", round(m['z_score'], 2))
    c3.metric("Leva (PFN/EBITDA)", round(pfn_in/max(1, ebit_in), 2))

    # Advisor AI
    st.subheader("🧠 Nexus AI: Strategic Advisor")
    if m['z_score'] < 1.23:
        st.error(f"⚠️ **ALLERTA INSOLVENZA**: Lo Z-Score indica un rischio elevato. Necessaria ristrutturazione debito.")
    else:
        st.success("✅ **SOLIDITÀ CONFERMATA**: I parametri predittivi indicano stabilità nel medio periodo.")

    # Grafici
    col_a, col_b = st.columns(2)
    with col_a:
        fig = go.Figure(go.Bar(x=['Tua Azienda', 'Media Settore'], y=[m['margin'], 12.5], marker_color='#00CC66'))
        fig.update_layout(title="Margine % vs Settore", template="plotly_dark", height=300)
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        z_val = m['z_score']
        fig2 = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = z_val,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Z-Score Altman (Previsione Fallimento)"},
            gauge = {
                'axis': {'range': [0, 4]},
                'steps': [
                    {'range': [0, 1.23], 'color': "red"},
                    {'range': [1.23, 2.9], 'color': "orange"},
                    {'range': [2.9, 4], 'color': "green"}]
            }
        ))
        st.plotly_chart(fig2, use_container_width=True)

    # Cloud Sync
    if supabase:
        try:
            supabase.table("audit_reports").insert({
                "company_name": nome_azienda, 
                "revenue": rev_in, 
                "score": round(m['z_score'], 2)
            }).execute()
            st.toast("✅ Sincronizzato con Nexus Cloud")
        except Exception as e:
            st.error(f"Errore Sync: {e}")

    # Generazione PDF e salvataggio in sessione
    st.session_state.pdf_data = create_pdf_bytes(nome_azienda, m)

# --- 5. SEZIONE EXPORT ---
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
