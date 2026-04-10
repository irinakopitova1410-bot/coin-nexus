import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime

# --- CONFIGURAZIONE UI ---
st.set_page_config(page_title="COIN-NEXUS CYBER-AUDIT", layout="wide")

# CSS TECHNO-SAFE (Design scuro e moderno)
st.markdown("""
    <style>
    .stApp { background-color: #05050a; color: #e0e6ed; }
    [data-testid="stSidebar"] { background-color: #0a0b15; border-right: 1px solid #1f2937; }
    
    /* Cyber Metrics */
    div[data-testid="stMetricValue"] { color: #3b82f6 !important; font-family: 'Courier New', monospace; font-weight: bold; }
    .stMetric { 
        background-color: #0f172a; 
        border: 1px solid #1e293b; 
        border-radius: 10px; 
        padding: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    
    /* Button Techno */
    .stButton>button {
        background: linear-gradient(90deg, #1e40af, #3b82f6);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 5px;
        font-weight: bold;
        transition: 0.3s;
        width: 100%;
    }
    .stButton>button:hover { box-shadow: 0 0 20px rgba(59, 130, 246, 0.6); transform: scale(1.02); }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #1e293b;
        border-radius: 5px 5px 0 0;
        color: white;
        padding:
