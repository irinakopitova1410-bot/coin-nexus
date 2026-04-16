import streamlit as st
import sys
import os

# 1. Trova la radice del progetto
root = os.path.dirname(os.path.abspath(__file__))

# 2. Aggiungi la radice al path se non c'è già
if root not in sys.path:
    sys.path.insert(0, root)

# 3. Import protetto (Evita la pagina bianca)
try:
    from engine.scoring import calculate_metrics
    from services.decision import get_credit_approval
    from utils.parser import extract_financials
except ImportError as e:
    st.error(f"❌ Errore critico di caricamento: {e}")
    st.stop() # Ferma l'app qui per non mostrare la pagina bianca
