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
    from utils.parser import extract_financials # Il tuo nuovo parser con Data Quality
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
    
    # Valori di default
    fin_data = {"revenue": 1000000, "ebitda": 200000, "debt": 400000, "short_debt": 100000, "data_quality": "n/a", "data_issues": []}

    if mode == "Upload ERP (Excel/CSV)":
        uploaded_file = st.file_uploader("Trascina qui il bilancio", type=["xlsx", "csv"])
        if uploaded_file:
            df = pd.read_excel(uploaded_file) if "xlsx" in uploaded_file.name else pd.read_csv(uploaded_file)
            # Utilizzo della tua funzione extract_financials
            extracted = extract_financials(df)
            fin_data.update(extracted)
            st.success(f"Qualità Dati: {fin_data['data_quality'].upper()}")

    st.divider()
    st.subheader("Parametri di Calcolo")
    isa_val = st.slider("Punteggio ISA (Affidabilità)", 1, 10, 8)
    rev_in = st.number_input("Ricavi (€)", value=int(fin_data.get('
