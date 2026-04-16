import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# --- 1. CONFIGURAZIONE E SETUP ---
st.set_page_config(page_title="Nexus Enterprise", layout="wide", page_icon="🏛️")

# Inizializzazione Session State per evitare errori di caricamento
if 'pdf_data' not in st.session_state:
    st.session_state.pdf_data = None
if 'metrics' not in st.session_state:
    st.session_state.metrics = None
if 'generated' not in st.session_state:
    st.session_state.generated = False

# --- 2. MOTORI DI CALCOLO (LOGICA FINANZIARIA) ---

def calculate_metrics(d):
    """Calcola i KPI base per l'analisi"""
    rev = max(d.get('revenue', 1), 1)
    ebitda = d.get('ebitda', 0)
    debt = d.get('debt', 0)
    # Calcolo DSCR semplificato
    dscr = ebitda / (debt * 0.1 + 1)
    margin = (ebitda / rev) * 100
    return {"dscr": dscr, "margin": margin, "ebitda": ebitda, "debt": debt, "revenue": rev}

def get_decision_engine(m):
    """Motore decisionale per approvazione fido"""
    score = 0
    if m['dscr'] > 1.25: score += 40
    if m['margin'] > 15: score += 30
    if m['ebitda'] > 500000: score += 30
    
    limit_credit = m['ebitda'] * 0.5 
    
    if score >= 70:
        return {"status": "APPROVATO", "color": "#00CC66", "limit": limit_credit}
    elif score >= 40:
        return {"status": "REVISIONE UMANA", "color": "#FFA500", "limit": limit_credit * 0.3}
    else:
        return {"status": "RESPINTO", "color": "#FF4B4B", "limit": 0}

def get_altman_z_score(m):
    """Previsione fallimento tramite Altman Z-Score"""
    # Parametri pesati per aziende private
    x1 = (m['revenue'] * 0.1) / max(m['debt'], 1) 
    x2 = (m['ebitda'] * 0.5) / max(m['debt'], 1)
    x3 = m['ebitda'] / max(m['debt'], 1)
    x4 = (m['revenue'] * 0.2) / max(m['debt'], 1)
    
    z = (1.2 * x1) + (1.4 * x2) + (3.3 * x3) + (0.6 * x4)
    
    if z > 2.9:
        return {"z": round(z, 2), "zone": "SICURA", "color": "#00CC66", "risk": "Basso"}
    elif z > 1.23:
        return {"z": round(z, 2), "zone": "GRIGIA", "color": "#FFA500", "risk": "Moderato"}
    else:
        return {"z": round(z, 2), "zone": "PERICOLO", "color": "#FF4B4B", "risk": "Alto (Default)"}

# --- 3. SIDEBAR (INPUT DATI) ---
with st.sidebar:
    st.title("🏛️ CFO Dashboard")
    st.markdown("Inserisci i dati contabili dell'azienda target.")
    
    nome_azienda = st.text_input("Ragione Sociale", "Azienda Target S.p.A.")
    rev_in = st.number_input("Fatturato (€)", value=1000000)
    ebit_in =
