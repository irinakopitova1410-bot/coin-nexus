import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client
from fpdf import FPDF
import io

# --- 1. CONFIGURAZIONE ---
st.set_page_config(page_title="Nexus Enterprise", layout="wide", page_icon="🏛️")

for key in ['pdf_data', 'generated', 'metrics']:
    if key not in st.session_state: st.session_state[key] = None

# --- 2. IL "CERVELLO" (DECISION ENGINE & Z-SCORE) ---

def calculate_metrics(d):
    rev = max(d.get('revenue', 1), 1)
    ebitda = d.get('ebitda', 0)
    debt = d.get('debt', 0)
    dscr = ebitda / (debt * 0.1 + 1)
    margin = (ebitda / rev) * 100
    return {"dscr": dscr, "margin": margin, "ebitda": ebitda, "debt": debt, "revenue": rev}

# RIGA 25: MOTORE DECISIONALE
def get_decision_engine(m):
    score = 0
    if m['dscr'] > 1.25: score += 40
    if m['margin'] > 15: score += 30
    if m['ebitda'] > 500000: score += 30
    limit = m['ebitda'] * 0.5 
    if score >= 70: return {"status": "APPROVATO", "color": "#00CC66", "limit": limit}
    elif score >= 40: return {"status": "REVISIONE", "color": "#FFA500", "limit": limit * 0.3}
    else: return {"status": "RESPINTO", "color": "#FF4B4B", "limit": 0}

# RIGA 36: PREVISIONE FALLIMENTO (ALTMAN Z-SCORE)
def get_altman_z_score(m):
    # Logica predittiva: X1-X4 basati su dati disponibili
    x1 = (m['revenue'] * 0.1) / max(m['debt'], 1) 
    x2 = (m['ebitda'] * 0.5) / max(m['debt'], 1)
    x3 = m['ebitda'] / max(m['debt'], 1)
    x4 = (m['revenue'] * 0.2) / max(m['debt'], 1)
    z = (1.2 * x1) + (1.4 * x2) + (3.3 * x3) + (0.6 * x4)
    
    if z > 2.9: return {"z": round(z,2), "zone": "SICURA", "color": "#00CC66", "risk": "Basso"}
    elif z > 1.23: return {"z": round(z,2), "zone": "GRIGIA", "color": "#FFA500", "risk": "Moderato"}
    else: return {"z": round(z,2), "zone": "PERICOLO", "color": "#FF4B4B", "risk": "Alto (Default)"}

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🏛️ CFO Dashboard")
    nome_azienda = st.text_input("Ragione Sociale", "Azienda Target S.p.A.")
    rev_in = st.number_input("Fatturato (€)", value=100000
