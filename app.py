import os
import sys
import streamlit as st

# --- FIX PERCORSI ---
# Ottiene la cartella principale del progetto
base_path = os.path.dirname(os.path.abspath(__file__))
# Aggiunge le sottocartelle al sistema di ricerca di Python
sys.path.insert(0, base_path)
sys.path.append(os.path.join(base_path, 'engine'))
sys.path.append(os.path.join(base_path, 'services'))
sys.path.append(os.path.join(base_path, 'utils'))

# --- IMPORT MODULI ---
try:
    from engine.scoring import calculate_metrics
    from services.decision import get_credit_approval
    from utils.parser import extract_financials
except ImportError as e:
    st.error(f"⚠️ Errore di inizializzazione: {e}")
    st.info("Assicurati che i file __init__.py siano presenti in ogni cartella.")
    st.stop()
