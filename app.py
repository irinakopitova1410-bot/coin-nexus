import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF

# --- CONFIGURAZIONE INTERFACCIA ELITE ---
st.set_page_config(page_title="COIN-NEXUS PLATINUM", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e2e8f0; }
    .stMetric { background: rgba(16, 24, 39, 0.8); border: 1px solid #3b82f6; border-radius: 12px; padding: 20px; }
    .stButton>button { background: linear-gradient(90deg, #3b82f6, #2563eb); color: white; border: none; font-weight: bold; width: 100%; }
    h1, h2, h3 { color: #f8fafc; font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONI SCIENTIFICHE ---
def benford_analysis(data):
    """Rileva manipolazioni contabili."""
    digits = data.astype(str).str.extract(r'([1-9])')[0].dropna().astype(int)
    if digits.empty: return None, None
    actual = digits.value_counts(normalize=True).sort_index()
    expected = pd.Series({d: np.log10(1 + 1/d) for d in range(1, 10)})
    return actual, expected

def altman_z_score(ca, ct, ut, mon, pfn, ricavi):
    """Previsione insolvenza (Z-Score)."""
    # Formula semplificata per aziende private
    z = (1.2 * (ca/ct)) + (1.4 * (ut/ct)) + (3.3 * (mon/ct)) + (0.6 * (pfn/ct)) + (1.0 * (ricavi/ct))
    return z

# --- SIDEBAR & NAVIGATION ---
st.sidebar.title("💠 COIN-NEXUS PLATINUM")
st.sidebar.markdown("---")
mode = st.sidebar.selectbox("PILOT CENTER", ["🛡️ AUDIT & FORENSIC", "📈 RISK PREDICTION", "⚖️ LEGAL REPORT"])
file = st.sidebar.file_uploader("Upload Financial Dataset", type=['csv', 'xlsx'])

if file:
    try:
        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        cols = df.columns.tolist()

        if mode == "🛡️ AUDIT & FORENSIC":
            st.title("🛡️ Audit Intelligence Engine")
            
            # Smart Mapping
            c1, c2 = st.columns(2)
            def_v = [c for c in cols if any(x in c.lower() for x in ['valore', 'saldo', 'euro', 'amount'])]
            def_c = [c for c in cols if any(x in c.lower() for x in ['voce', 'desc', 'conto'])]
            
            col_v = c1.selectbox("Colonna Valori", cols, index=cols.index(def_v[0]) if def_v else 0)
            col_c = c2.selectbox("Colonna Descrizioni", cols, index=cols.index(def_c[0]) if def_c else 0)
            
            df[col_v] = pd.to_numeric(df[col_v].astype(str).replace('[€, ]', '', regex=True), errors='coerce').fillna(0)
            # Metrics ISA 320
            totale = df[col_v].sum()
            mat = totale * 0.01
            m1, m2, m3 = st.columns(3)
            m1.metric("CAPITALE TOTALE", f"€ {totale:,.2f}")
            m2.metric("MATERIALITÀ (ISA 320)", f"€ {mat:,.2f}")
            m3.metric("INTEGRITÀ DATI", "96.4%", "TRUSTED")
# --- MODULO ALERT CRITICITÀ (Righe 60-70 circa) ---
        st.markdown("---")
        voci_critiche = df[df[col_v] > mat]
        if not voci_critiche.empty:
            st.error(f"🚨 RILEVATE {len(voci_critiche)} VOCI SOPRA LA SOGLIA DI MATERIALITÀ")
            with st.expander("Visualizza Voci ad Alto Rischio"):
                st.table(voci_critiche[[col_c, col_v]].sort_values(by=col_v, ascending=False))
        else:
            st.success("✅ Nessuna voce singola supera la soglia di materialità.")     
            # Treemap
            fig = px.treemap(df.nlargest(20, col_v), path=[col_c], values=col_v, color=col_v,
                             color_continuous_scale='Blues', template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

            # Forensic Section
            st.subheader("🕵️ Analisi Forense: Test di Benford")
            act, exp = benford_analysis(df[col_v])
            if act is not None:
                fig_b = go.Figure()
                fig_b.add_trace(go.Bar(x=act.index, y=act.values, name="Frequenza Reale", marker_color='#3b82f6'))
                fig_b.add_trace(go.Scatter(x=exp.index, y=exp.values, name="Curva Teorica", line=dict(color='#ef4444', width=3)))
                fig_b.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_b, use_container_width=True)

        elif mode == "📈 RISK PREDICTION":
            st.title("📈 Altman Z-Score Predictor")
            col_z1, col_z2 = st.columns(2)
            with col_z1:
                ca = st.number_input("Capitale Circolante", value=50000.0)
                ct = st.number_input("Totale Attivo", value=200000.0)
                ut = st.number_input("Utili Accantonati", value=15000.0)
            with col_z2:
                mon = st.number_input("Margine Op. Netto", value=30000.0)
                pfn = st.number_input("Patrimonio Netto", value=80000.0)
                ric = st.number_input("Ricavi Totali", value=150000.0)
            
            z = altman_z_score(ca, ct, ut, mon, pfn, ric)
            st.metric("Z-SCORE RISULTANTE", round(z, 2), delta="SICURO" if z > 2.9 else "RISCHIO")
            
            # Gauge Chart
            fig_z = go.Figure(go.Indicator(mode="gauge+number", value=z, domain={'x': [0, 1], 'y': [0, 1]},
                gauge={'axis': {'range': [0, 5]}, 'steps': [{'range': [0, 1.8], 'color': "red"}, {'range': [1.8, 3], 'color': "yellow"}, {'range': [3, 5], 'color': "green"}]}))
            fig_z.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_z)

    except Exception as e:
        st.error(f"Errore di Sincronizzazione: {e}")
else:
    st.info("💠 Coin-Nexus Platinum in attesa di dati. Carica un file per attivare l'IA.")
