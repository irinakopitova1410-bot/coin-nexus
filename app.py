import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import io

# --- 1. CONFIGURAZIONE ---
st.set_page_config(page_title="Nexus Enterprise | AI Financial Hub", layout="wide", page_icon="🏛️")

if 'pdf_data' not in st.session_state:
    st.session_state.pdf_data = None

# --- 2. MOTORE DI ESTRAZIONE E ANALISI ---

def extract_financials(df):
    """Mappa automaticamente le colonne del bilancio ERP/Excel"""
    cols = {c.lower(): c for c in df.columns}
    data = {"rev": 1000000, "ebit": 200000, "debt": 400000} # Default
    
    mapping = {
        "rev": ['fatturato', 'revenue', 'vendite', 'valore della produzione'],
        "ebit": ['ebitda', 'mol', 'margine operativo lordo'],
        "debt": ['debito', 'debt', 'pfn', 'debiti finanziari']
    }
    
    for key, aliases in mapping.items():
        for alias in aliases:
            if alias in cols:
                data[key] = pd.to_numeric(df[cols[alias]], errors='coerce').sum()
                break
    return data

def run_analysis(rev, ebitda, debt):
    rev = max(rev, 1)
    # Altman Z-Score
    z = (1.2 * (rev*0.1/max(debt,1))) + (3.3 * (ebitda/max(debt,1)))
    # Credit Metrics
    pd_rate = max(0.01, min(0.99, 1 / (z + 0.1) * 0.2))
    expected_loss = (rev * 0.10) * pd_rate * 0.45
    suggested_rate = (0.05 + pd_rate + 0.02) * 100
    
    status = "ECCELLENTE" if z > 2.6 else "STABILE" if z > 1.1 else "CRITICA"
    color = "#00CC66" if z > 2.6 else "#FFA500" if z > 1.1 else "#FF4B4B"
    
    return {
        "z": z, "status": status, "color": color, 
        "pd": pd_rate * 100, "el": expected_loss, "rate": suggested_rate,
        "ros": (ebitda/rev)*100, "lev": debt/max(ebitda,1)
    }

# --- 3. SIDEBAR: CARICAMENTO ERP E INPUT ---
with st.sidebar:
    st.title("🏛️ Nexus Control Panel")
    st.subheader("📂 Importa Bilancio (ERP)")
    uploaded_file = st.file_uploader("Carica Excel o CSV", type=["xlsx", "csv"])
    
    # Valori iniziali
    defaults = {"rev": 1000000, "ebit": 200000, "debt": 400000}
    
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file) if "xlsx" in uploaded_file.name else pd.read_csv(uploaded_file)
            defaults = extract_financials(df)
            st.success("✅ Dati ERP estratti!")
        except Exception as e:
            st.error(f"Errore lettura: {e}")

    st.divider()
    nome = st.text_input("Ragione Sociale", "Azienda Target S.p.A.")
    rev_in = st.number_input("Fatturato (€)", value=int(defaults['rev']))
    ebit_in = st.number_input("EBITDA (€)", value=int(defaults['ebit']))
    pfn_in = st.number_input("Debito Finanziario (€)", value=int(defaults['debt']))
    
    st.divider()
    opt_deep = st.toggle("🔍 Attiva Deep Audit", value=True)
    opt_credit = st.toggle("🎯 Analisi Rischio & Pricing", value=True)

# --- 4. MAIN INTERFACE ---
st.title("📊 Financial Intelligence & Credit Risk Analysis")

if st.button("🚀 ESEGUI ANALISI GLOBALE", use_container_width=True):
    res = run_analysis(rev_in, ebit_in, pfn_in)
    
    # Sezione 1: Rating & Solvibilità
    st.header(f"🏢 Report: {nome}")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div style='background:{res['color']};padding:25px;border-radius:15px;text-align:center;color:white;'><h1>{res['status']}</h1></div>", unsafe_allow_html=True)
    c2.metric("Altman Z-Score", f"{res['z']:.2f}", help="Punteggio predittivo di insolvenza")
    c3.metric("Leva Finanziaria", f"{res['lev']:.2f}x", delta="Sostenibile" if res['lev'] < 4 else "Elevata", delta_color="inverse")

    # Sezione 2: Deep Audit (Opzionale)
    if opt_deep:
        st.divider()
        st.subheader("🕵️ Analisi Tecnica di Bilancio")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.metric("Redditività (ROS)", f"{res['ros']:.1f}%")
            fig_ros = go.Figure(go.Indicator(mode="gauge+number", value=res['ros'], gauge={'axis': {'range': [None, 30]}, 'bar': {'color': "#00CC66"}}))
            fig_ros.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig_ros, use_container_width=True)
        with col_d2:
            st.write("**Commento Tecnico AI:**")
            if res['ros'] > 15: st.success("L'azienda genera margini elevati rispetto al settore.")
            else: st.warning("Marginalità sotto la media: analizzare i costi operativi.")

    # Sezione 3: Credit Pricing (Opzionale)
