import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF

# --- 1. SETUP ---
st.set_page_config(page_title="Nexus Enterprise | Deep Audit", layout="wide", page_icon="🏛️")

# --- 2. MOTORI DI CALCOLO ---
def run_basic_analysis(rev, ebitda, debt):
    rev = max(rev, 1)
    z = (1.2 * (rev*0.1/max(debt,1))) + (3.3 * (ebitda/max(debt,1))) # Altman semplificato
    status = "SICURA" if z > 2.6 else "REVISIONE" if z > 1.1 else "PERICOLO"
    color = "#00CC66" if status == "SICURA" else "#FFA500" if status == "REVISIONE" else "#FF4B4B"
    return {"z": z, "status": status, "color": color}

def run_deep_audit(rev, ebitda, debt):
    # Calcolo indici di bilancio professionali
    ros = (ebitda / max(rev, 1)) * 100
    leverage = debt / max(ebitda, 1)
    break_even = (rev * 0.7) # Stima del punto di pareggio
    return {"ros": ros, "leverage": leverage, "bep": break_even}

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🏛️ Nexus Dashboard")
    nome = st.text_input("Ragione Sociale", "Azienda Target S.p.A.")
    rev_in = st.number_input("Fatturato (€)", value=1000000)
    ebit_in = st.number_input("EBITDA (€)", value=200000)
    pfn_in = st.number_input("Debito (€)", value=400000)
    
    st.divider()
    # L'OPZIONE CHE HAI CHIESTO:
    deep_audit_mode = st.toggle("🔍 Attiva Deep Audit (Analisi Bilancio)")
    st.caption("La modalità Deep Audit analizza redditività e sostenibilità nel dettaglio.")

# --- 4. MAIN UI ---
st.title("📊 Financial Intelligence Engine")

if st.button("🚀 GENERA ANALISI", use_container_width=True):
    # Analisi Base sempre visibile
    res = run_basic_analysis(rev_in, ebit_in, pfn_in)
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(f"""<div style='background:{res['color']};padding:25px;border-radius:15px;text-align:center;color:white;'>
                    <h1 style='margin:0;'>{res['status']}</h1><p style='margin:0;'>Z-Score: {res['z']:.2f}</p></div>""", unsafe_allow_html=True)
    with c2:
        st.metric("Punteggio Solvibilità", f"{res['z']:.2f}/4.0")

    # SEZIONE OPZIONALE: DEEP AUDIT
    if deep_audit_mode:
        st.divider()
        st.subheader("🕵️ Analisi Tecnica di Bilancio (Deep Audit)")
        audit = run_deep_audit(rev_in, ebit_in, pfn_in)
        
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Redditività (ROS)", f"{audit['ros']:.1f}%")
        col_b.metric("Leva Finanziaria", f"{audit['leverage']:.2f}x")
        col_c.metric("Punto di Pareggio (est.)", f"€ {audit['bep']:,.0f}")
        
        # Grafico Radar per il Deep Audit
        st.write("### Posizionamento Strategico")
        fig = go.Figure(data=go.Scatterpolar(
            r=[audit['ros'], audit['leverage']*10, 20],
            theta=['Redditività','Solvibilità','Efficienza'],
            fill='toself',
            marker=dict(color=res['color'])
        ))
        st.plotly_chart(fig, use_container_width=True)
    
    # --- RADAR PORTAFOGLIO (Sempre presente per Doc Finance) ---
    st.divider()
    st.header("🛰️ Portfolio View")
    portfolio_df = pd.DataFrame({
        'Azienda': [nome, 'Beta Corp', 'Gamma SpA'],
        'Score': [res['z'], 1.5, 0.8]
    })
    st.dataframe(portfolio_df, use_container_width=True)
