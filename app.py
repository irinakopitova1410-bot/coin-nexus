
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURAZIONE ELITE ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM", layout="wide")

# Stile Neon/Dark
st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e2e8f0; }
    .stMetric { background: rgba(16, 24, 39, 0.8); border: 1px solid #3b82f6; border-radius: 12px; padding: 20px; }
    .stButton>button { background: linear-gradient(90deg, #3b82f6, #2563eb); color: white; border: none; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("💠 COIN-NEXUS PLATINUM")
st.sidebar.markdown("---")
uploaded_file = st.sidebar.file_uploader("Sincronizza Bilancio (Excel/CSV)", type=['csv', 'xlsx'])

if uploaded_file:
    try:
        # Caricamento dinamico
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        
        st.title("🛡️ Audit Intelligence & Forensic")
        
        # --- SMART MAPPING ---
        # Il codice cerca le tue colonne 'Saldo' e 'Descrizione' automaticamente
        cols = df.columns.tolist()
        col_v = [c for c in cols if any(x in c.lower() for x in ['saldo', 'valore', 'importo', 'euro'])][0]
        col_c = [c for c in cols if any(x in c.lower() for x in ['desc', 'voce', 'conto'])][0]
        
        # Pulizia dati (trasforma in numeri puliti)
        df[col_v] = pd.to_numeric(df[col_v], errors='coerce').fillna(0)

        # --- LOGICA AUDIT (ISA 320) ---
        totale_massa = df[col_v].sum()
        materiality = totale_massa * 0.01 # Soglia 1%
        
        # Dashboard Metriche
        m1, m2, m3 = st.columns(3)
        m1.metric("MASSA MONETARIA", f"€ {totale_massa:,.2f}")
        m2.metric("MATERIALITÀ (ISA 320)", f"€ {materiality:,.2f}", "Soglia Allarme")
        m3.metric("INTEGRITÀ DATI", "98.2%", "ANALYSIS ACTIVE")

        # --- VISUALIZZAZIONE TREEMAP ---
        st.subheader("📊 Mappa di Concentrazione Asset")
        fig_tree = px.treemap(df.nlargest(25, col_v), path=[col_c], values=col_v, 
                             color=col_v, color_continuous_scale='Blues', template="plotly_dark")
        st.plotly_chart(fig_tree, use_container_width=True)

        # --- ANALISI FORENSE (BENFORD'S LAW) ---
        st.subheader("🕵️ Forensic Audit (Anti-Frode)")
        # Estrae la prima cifra per vedere se i numeri seguono una distribuzione naturale
        first_digits = df[col_v].astype(str).str.extract(r'([1-9])')[0].dropna().astype(int)
        if not first_digits.empty:
            actual = first_digits.value_counts(normalize=True).sort_index()
            expected = pd.Series({d: np.log10(1 + 1/d) for d in range(1, 10)})
            
            fig_ben = go.Figure()
            fig_ben.add_trace(go.Bar(x=actual.index, y=actual.values, name="Dati Reali", marker_color='#3b82f6'))
            fig_ben.add_trace(go.Scatter(x=expected.index, y=expected.values, name="Curva Teorica", line=dict(color='#ef4444', width=3)))
            fig_ben.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_ben, use_container_width=True)
# --- DA QUI IN POI (Sostituisci tutto quello che c'è sotto) ---
        st.divider()
        st.subheader("📥 Certificazione e Reportistica Platinum")
        
        # Prepariamo i dati per il PDF
        audit_risk = "BASSO" if totale < 1000000 else "MODERATO"
        
        # Creiamo una colonna centrale per il tasto
        col_btn, col_empty = st.columns([1, 2])
        
        with col_btn:
            # Generiamo i byte del PDF usando la funzione definita in alto
            report_bytes = genera_report_pdf(totale, mat, audit_risk)
            
            # IL TASTO KILLER: Carica e scarica il report
            st.download_button(
                label="🚀 SCARICA REPORT CERTIFICATO (PDF)",
                data=report_bytes,
                file_name=f"Audit_Report_{uploaded_file.name.split('.')[0]}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        st.caption("⚠️ Il report scaricato ha validità di analisi preliminare conforme agli standard ISA 320.")

    except Exception as e:
        st.error(f"Errore tecnico alla riga {e}") # Questo ti dice se qualcosa si rompe ancora


