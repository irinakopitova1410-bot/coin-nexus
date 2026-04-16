import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import io

# --- 1. SETUP ---
st.set_page_config(page_title="Nexus Enterprise", layout="wide", page_icon="🏛️")

if 'pdf_data' not in st.session_state:
    st.session_state.pdf_data = None

# --- 2. LOGICA ESTRAZIONE DATI ERP ---
def extract_from_file(df):
    """Cerca automaticamente le colonne finanziarie nel file caricato"""
    cols = {c.lower(): c for c in df.columns}
    data = {}
    # Cerca Fatturato
    for k in ['fatturato', 'revenue', 'vendite', 'valore della produzione']:
        if k in cols: 
            data['rev'] = pd.to_numeric(df[cols[k]], errors='coerce').sum()
            break
    # Cerca EBITDA
    for k in ['ebitda', 'mol', 'margine operativo lordo']:
        if k in cols: 
            data['ebit'] = pd.to_numeric(df[cols[k]], errors='coerce').sum()
            break
    # Cerca Debito
    for k in ['debito', 'debt', 'pfn', 'debiti']:
        if k in cols: 
            data['debt'] = pd.to_numeric(df[cols[k]], errors='coerce').sum()
            break
    return data

# --- 3. MOTORE DI CALCOLO (CERVELLO) ---
def run_analysis(rev, ebitda, debt):
    rev = max(rev, 1)
    # Altman Z-Score (PMI)
    x1 = (rev * 0.1) / max(debt, 1)
    x2 = (ebitda * 0.5) / max(debt, 1)
    z = (1.2 * x1) + (1.4 * x2) + (3.3 * (ebitda / max(debt, 1)))
    
    if z > 2.6: status, color = "APPROVATO", "#00CC66"
    elif z > 1.1: status, color = "REVISIONE", "#FFA500"
    else: status, color = "RESPINTO", "#FF4B4B"
    
    return {"z": z, "status": status, "color": color, "limit": ebitda * 0.5}

# --- 4. SIDEBAR CON CARICAMENTO FILE ---
with st.sidebar:
    st.title("🏛️ CFO Panel")
    st.subheader("📂 Importa Dati ERP")
    uploaded_file = st.file_uploader("Carica Excel o CSV", type=["xlsx", "csv"])
    
    # Valori di default
    default_rev, default_ebit, default_debt = 1000000, 200000, 400000
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.xlsx'):
                df_erp = pd.read_excel(uploaded_file)
            else:
                df_erp = pd.read_csv(uploaded_file)
            
            extracted = extract_from_file(df_erp)
            if 'rev' in extracted: default_rev = int(extracted['rev'])
            if 'ebit' in extracted: default_ebit = int(extracted['ebit'])
            if 'debt' in extracted: default_debt = int(extracted['debt'])
            st.success("✅ Dati estratti con successo!")
        except Exception as e:
            st.error(f"Errore nella lettura del file: {e}")

    st.divider()
    nome = st.text_input("Ragione Sociale", "Azienda Target S.p.A.")
    rev_in = st.number_input("Fatturato (€)", value=default_rev)
    ebit_in = st.number_input("EBITDA (€)", value=default_ebit)
    pfn_in = st.number_input("Debito (€)", value=default_debt)

# --- 5. MAIN UI ---
st.title("📊 Nexus Enterprise: AI Risk Intelligence")

if st.button("🚀 GENERA ANALISI E AGGIORNA RADAR", use_container_width=True):
    res = run_analysis(rev_in, ebit_in, pfn_in)
    
    # KPI Singola Azienda
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div style='background:{res['color']};padding:20px;border-radius:10px;text-align:center;color:white;'><h2>{res['status']}</h2></div>", unsafe_allow_html=True)
    col2.metric("Altman Z-Score", round(res['z'], 2))
    col3.metric("Fido Massimo", f"€ {res['limit']:,.0f}")

    # --- SEZIONE PORTAFOGLIO ---
    st.divider()
    st.header("🛰️ Portfolio Radar (Market View)")
    
    portfolio_df = pd.DataFrame({
        'Azienda': [nome, 'Client_B', 'Client_C', 'Client_D'],
        'Z-Score': [res['z'], 1.45, 0.82, 2.95],
        'Status': [res['status'], 'REVISIONE', 'PERICOLO', 'SICURA']
    })

    tab_radar, tab_list = st.tabs(["🌍 Mappa del Rischio", "📋 Elenco Posizioni"])
    
    with tab_radar:
        fig = go.Figure(go.Scatter(
            x=portfolio_df['Azienda'], y=portfolio_df['Z-Score'],
            mode='markers+text', text=portfolio_df['Status'],
            textposition="top center",
            marker=dict(size=40, color=['#00CC66' if s in ['APPROVATO', 'SICURA'] else '#FF4B4B' if s == 'PERICOLO' else '#FFA500' for s in portfolio_df['Status']])
        ))
        fig.update_layout(height=400, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with tab_list:
        st.dataframe(portfolio_df, use_container_width=True)

    # PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(0, 10, f"Dossier Nexus: {nome}", ln=True)
    st.session_state.pdf_data = bytes(pdf.output())

# --- 6. EXPORT ---
st.divider()
if st.session_state.pdf_data:
    st.download_button("📄 SCARICA REPORT PDF", st.session_state.pdf_data, "Nexus_Report.pdf", "application/pdf", use_container_width=True)
