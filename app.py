import streamlit as st
import requests
import pandas as pd
from io import BytesIO

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="Nexus Engine | Fintech Dashboard",
    page_icon="🏛️",
    layout="wide"
)

# --- 2. STILE CSS PERSONALIZZATO ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007BFF; color: white; }
    .metric-container { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR E ACCESSO (MULTI-TENANT) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135706.png", width=80)
    st.title("🔐 Nexus Access")
    api_key_input = st.text_input("Enterprise API Key", value="nexus_test_key_2026", type="password")
    st.divider()
    st.info("Piano: **PRO Enterprise**")
    st.caption("v1.2.0 - Fintech Grade")

# --- 4. INPUT DATI ---
st.title("🏛️ Nexus Business Intelligence")
st.subheader("Analisi Merito Creditizio Basilea IV")

with st.container():
    col_a, col_b = st.columns([2, 1])
    with col_a:
        nome_az = st.text_input("Ragione Sociale Azienda", value="Azienda Beta S.p.A.")
    with col_b:
        data_analisi = st.date_input("Data Valutazione")

col_in1, col_in2, col_in3 = st.columns(3)
with col_in1:
    rev = st.number_input("Fatturato Lordo (€)", value=1500000.0, step=10000.0)
with col_in2:
    ebit = st.number_input("EBITDA (€)", value=250000.0, step=5000.0)
with col_in3:
    pfn = st.number_input("PFN (Debito Totale) (€)", value=400000.0, step=10000.0)

# --- 5. LOGICA DI CALCOLO E RATING DESIGN ---
# Calcolo rapido Z-Score locale
denominatore = pfn if pfn > 0 else 1
z = (1.2 * (rev * 0.1 / denominatore)) + (3.3 * (ebit / denominatore))

if z > 2.6:
    rating_label = "SOLIDO"
    rating_color = "#28a745" # Verde
    bg_color = "#d4edda"
elif z > 1.1:
    rating_label = "VULNERABILE"
    rating_color = "#ffc107" # Giallo/Arancio
    bg_color = "#fff3cd"
else:
    rating_label = "DISTRESSED"
    rating_color = "#dc3545" # Rosso
    bg_color = "#f8d7da"

# --- 6. VISUALIZZAZIONE RISULTATI (DESIGN ORIGINALE) ---
st.write("")
st.markdown(
    f"""
    <div style="background-color:{bg_color}; padding:25px; border-radius:12px; border-left: 10px solid {rating_color};">
        <h1 style="color:{rating_color}; margin:0; font-size: 40px;">RATING: {rating_label}</h1>
        <p style="color:#333; font-size:20px; margin:0;">Z-Score Basilea IV: <strong>{z:.2f}</strong></p>
    </div>
    """, 
    unsafe_allow_html=True
)
st.write("")

# Metriche Dashboard
m1, m2, m3 = st.columns(3)
with m1: st.metric("Fatturato", f"€ {rev:,.0f}")
with m2: st.metric("EBITDA", f"€ {ebit:,.0f}")
with m3: st.
