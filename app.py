import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime

# --- CONFIGURAZIONE INTERFACCIA TECHNO ---
st.set_page_config(page_title="COIN-NEXUS CYBER-AUDIT", layout="wide", page_icon="🕵️")

# CSS Avanzato per Look Techno-Futuristico
st.markdown("""
    <style>
    /* Font principale e Sfondo Deep Black */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #050509;
        color: #e0e6ed;
    }

    /* Sidebar Scura e Pulita */
    [data-testid="stSidebar"] {
        background-color: #0a0b14;
        border-right: 1px solid #1f293a;
    }

    /* Metriche stile 'Cyber-Panel' con Glow */
    .stMetric {
        background: rgba(16, 20, 35, 0.6);
        border: 1px solid #1f293a;
        border-radius: 12px;
        padding: 25px;
        transition: all 0.3s ease-in-out;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .stMetric:hover {
        border-color: #3b82f6;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
        transform: translateY(-2px);
    }
    .stMetric label { color: #818cf8 !important; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
    .stMetric .stNumberValue { color: #ffffff !important; font-weight: 700; font-size: 2.2rem !important; }

    /* Pulsanti Techno con Gradiente */
    .stButton>button {
        background: linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.2s;
        width: 100%;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
        box-shadow: 0 0 20px rgba(96, 165, 250, 0.6);
    }

    /* Tab Design scuro */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #0a0b14;
        border-radius: 8px;
        padding: 5px;
        border: 1px solid #1f293a;
    }
    .stTabs [data-baseweb="tab"] {
        color: #9ca3af;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        color: #3b82f6 !important;
        background-color: #111827;
        border-radius: 6px;
    }

    /* Input e Slider */
    .stSlider [data-baseweb="slider"] { color: #3b82f6; }
    .stTextInput>div>div>input {
        background-color: #111827;
        border: 1px solid #1f293a;
        color: white;
        border-radius: 6px;
    }

    /* Warning Alert color magenta techno */
    .stAlert {
        background-color: #1e1b2e;
        color: #f472b6;
        border: 1px solid #f472b6;
        border-radius: 8px;
    }
    
    /* Header pulsante */
    h1, h2, h3 {
        color: #ffffff;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE ANALISI AVANZATA ---
def check_data_integrity(df, col_v):
    issues = []
    if df[col_v].isnull().any(): issues.append(f"📡 Rilevati {df[col_v].isnull().sum()} pacchetti dati mancanti (NULL).")
    if (df[col_v] == 0).any(): issues.append(f"📉 Rilevati { (df[col_v] == 0).sum() } valori zero (Sospetto Window Dressing).")
    if (df[col_v] < 0).any(): issues.append("⚠️ Valori negativi individuati (Verificare storni).")
    return issues

def benford_analysis(data):
    digits = data.abs().astype(str).
