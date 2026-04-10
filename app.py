import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime

# --- CONFIGURAZIONE INTERFACCIA ---
st.set_page_config(page_title="COIN-NEXUS CYBER-AUDIT", layout="wide")

# CSS TECHNO-MODERN (Deep Black & Neon Blue)
st.markdown("""
    <style>
    /* Sfondo e Testo */
    .stApp { background-color: #050505; color: #ffffff; }
    
    /* Sidebar Professionale */
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #333; }
    
    /* Metriche stile Dashboard Navale */
    div[data-testid="stMetricValue"] { color: #00d4ff !important; font-family: 'Monaco', monospace; font-size: 2rem !important; }
    .stMetric { 
        background-color: #111; 
        border: 1px solid #222; 
        border-radius: 4px; 
        padding: 20px;
        box-shadow: inset 0 0 10px rgba(0, 212, 255, 0.05);
    }
    
    /* Pulsanti ad alto contrasto */
    .stButton>button {
        background: transparent;
        color: #00d4ff;
        border: 1px solid #00d4ff;
        border-radius: 2px;
        font-weight: bold;
        transition: all 0.3s;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .stButton>button:hover {
        background: #00d4ff;
        color: #000;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.4);
    }

    /* Tabs Minimaliste */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; gap: 10px;
