import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. Configurazione Iniziale
st.set_page_config(page_title="Coin-Nexus | Advanced Intelligence", layout="wide", page_icon="🏛️")

# 2. Fix Path per moduli locali
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from engine.scoring import calculate_metrics
    from services.decision import get_credit_approval
    from utils.parser import extract_financials 
except ImportError as e:
    st.error(f"⚠️ Errore Configurazione: {e}. Verifica i file __init__.py nelle cartelle.")
    st.stop()

# --- LOGICA REPORT AVANZATO ---
def get_advanced_report(metrics, isa_score):
    rev = metrics.get('revenue', 0)
    materiality = rev * 0.015 # Standard ISA 320
    dscr = metrics.get('dscr', 0)
    
    if dscr > 1.4 and isa_score >= 8:
        solidity, color = "ECCELLENTE", "#00CC66"
    elif dscr >= 1.1:
        solidity, color = "STABILE", "#FFCC00"
    else:
        solidity, color = "VULNERABILE", "#FF3300"
        
    return {"materiality": materiality, "solidity_4y": solidity, "color": color}

# --- SIDEBAR: CARICAMENTO E INPUT ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/library.png", width=80)
    st.title("Nexus Data Source")
    
    mode = st.radio("Sorgente Dati:", ["Upload ERP (Excel/CSV)", "Inserimento Manuale"])
    
    # Inizializzazione dati di default
    fin_data = {
        "revenue": 1000000, 
        "ebitda": 200000, 
        "debt": 400000, 
        "short_debt": 100000, 
        "data_quality": "n/a", 
        "data_issues": []
    }

    if mode == "Upload ERP (Excel/CSV)":
        uploaded_file = st.file_uploader("Trascina qui il bilancio", type=["xlsx", "csv"])
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file) if "xlsx" in uploaded_file.name else pd.read_csv(uploaded_file)
                extracted = extract_financials(df)
                fin_data.update(extracted)
                st.success(f"Qualità Dati: {fin_data['data_quality'].upper()}")
            except Exception as e:
                st.error(f"Errore caricamento: {e}")

    st.divider()
    st.subheader("Parametri di Calcolo")
    isa_val = st.slider("Punteggio ISA (Affidabilità)", 1, 10, 8)
    
    # Fix SyntaxError: stringhe e parentesi chiuse correttamente
    rev_in = st.number_input("Ricavi (€)", value=int(fin_data.get('revenue', 1000000)))
    ebit_in = st.number_input("EBITDA (€)", value=int(fin_data.get('ebitda', 200000)))
    debt_in = st.number_input("Debito Totale (€)", value=int(fin_data.get('debt', 400000)))
    short_in = st.number_input("Debito Breve (€)", value=int(fin_data.get('short_debt', 100000)))

# --- DASHBOARD PRINCIPALE ---
st.title("🏛️ Coin-Nexus | Financial Intelligence Audit")
st.caption("Analisi Forward-Looking a 48 mesi e Materialità ISA 320")

if st.button("ESEGUI AUDIT PROFESSIONALE", type="primary", use_container_width=True):
    # Esecuzione Motore di Calcolo
    m = calculate_metrics({"revenue": rev_in, "ebitda": ebit_in, "debt": debt_in, "short_debt": short_in})
    res = get_credit_approval(m)
    audit = get_advanced_report(m, isa_val)
    
    # SEZIONE 1: ANALISI QUALITÀ DATI
    st.subheader("🔍 Data Quality Audit")
    q_col1, q_col2 = st.columns([1, 3])
    with q_col1:
        st.metric("CONFIDENCE", str(fin_data.get('data_quality', 'N/A')).upper())
    with q_col2:
        issues = fin_data.get('data_issues', [])
        if issues:
            for issue in issues:
                st.warning(f"Rilevato: {issue}")
        else:
            st.success("✅ Nessuna anomalia contabile rilevata nel file ERP.")

    st.divider()

    # SEZIONE 2: KPI RATING & MATERIALITÀ
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("RATING", res.get('rating', 'N/D'))
        st.write(f"Esito: **{res.get('decision', 'In attesa')}**")
    with col2:
        st.metric("SCORE", f"{res.get('score', 0)}/100")
        st.write(f"Materialità ISA: **€ {audit['materiality']:,.0f}**")
    with col3:
        st.metric("SOLIDITÀ 4 ANNI", audit['solidity_4y'])
        st.write(f"Capacità Credito: **€ {res.get('estimated_credit', 0):,}**")

    # SEZIONE 3: GRAFICI PROSPETTICI
    st.subheader("📊 Stress Test: Sostenibilità Debito (DSCR) 2026-2030")
    anni = ['Oggi', '2027', '2028', '2029', '2030']
    base_dscr = m.get('dscr', 0)
    proiezione = [base_dscr, base_dscr*1.05, base_dscr*1.1, base_dscr*1.08, base_dscr*1.12]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=anni, y=proiezione, mode='lines+markers', 
                             line=dict(color=audit['color'], width=4), name="DSCR Previsto"))
    fig.add_hline(y=1.2, line_dash="dash", line_color="red", annotation_text="Soglia Alert")
    fig.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.success(f"**Giudizio Finale:** L'impresa presenta una struttura finanziaria {audit['solidity_4y']}.")

else:
    st.info("Configura i parametri o carica un file ERP per generare l'audit completo.")
