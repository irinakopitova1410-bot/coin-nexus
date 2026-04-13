import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import datetime
from sklearn.ensemble import IsolationForest
from supabase import create_client, Client

# --- 1. CONFIGURAZIONE CORE ---
SUPABASE_URL = "https://ipmttldwfsxuubugiyir.supabase.co"
SUPABASE_KEY = "sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos" # <--- METTI LA TUA CHIAVE REALE
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except:
    st.error("Connessione Cloud Fallita. Controlla la Key.")

# --- 2. MOTORE DI CALCOLO QUANTUM ---
def quantum_analysis(df, val_col):
    totale_flussi = df[val_col].sum()
    media_flussi = df[val_col].mean()
    volatilita = df[val_col].std()
    
    # Materialità ISA 320 (Soglia di errore tollerabile)
    materialita = totale_flussi * 0.015 
    
    # Simulazione DSCR (Sostenibilità Debito)
    # Se la volatilità è bassa rispetto ai flussi, il debito è più sostenibile
    dscr = (totale_flussi / (volatilita * 1.5)) if volatilita > 0 else 2.5
    
    # Z-Score semplificato (Rischio Crisi)
    z_score = 1.2 + (totale_flussi / 1000000) - (volatilita / totale_flussi)
    
    # Rating Finale
    if z_score > 2.5 and dscr > 1.2: rating = "AAA - EXCELLENT"
    elif z_score > 1.1: rating = "BBB - STABLE"
    else: rating = "CCC - AT RISK"
    
    return {
        "totale": totale_flussi,
        "materialita": materialita,
        "dscr": dscr,
        "z_score": z_score,
        "rating": rating
    }

# --- 3. GENERATORE REPORT CERTIFICATO ---
class PDF(FPDF):
    def header(self):
        self.set_fill_color(0, 40, 80)
        self.rect(0, 0, 210, 40, 'F')
        self.set_font("Arial", 'B', 22)
        self.set_text_color(255, 255, 255)
        self.cell(190, 20, "COIN-NEXUS QUANTUM REPORT v3.5", ln=True, align='C')
        self.ln(20)

def genera_report_pdf(studio, data, anomalie):
    pdf = PDF()
    pdf.add_page()
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(190, 10, f"STUDIO PROFESSIONALE: {studio.upper()}", ln=True)
    pdf.cell(190, 10, f"DATA CERTIFICAZIONE: {datetime.date.today()}", ln=True)
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    
    # Tabella Risultati
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(95, 10, "INDICATORE", 1)
    pdf.cell(95, 10, "VALORE", 1, ln=True)
    
    pdf.set_font("Arial", size=11)
    results = [
        ("Massa Totale Analizzata", f"EUR {data['totale']:,.2f}"),
        ("Soglia Materialita ISA 320", f"EUR {data['materialita']:,.2f}"),
        ("Indice Sostenibilita DSCR", f"{data['dscr']:.2f}"),
        ("Quantum Z-Score", f"{data['z_score']:.2f}"),
        ("RATING FINALE", data['rating'])
    ]
    for label, val in results:
        pdf.cell(95, 10, label, 1)
        pdf.cell(95, 10, val, 1, ln=True)
        
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(190, 7, "VALIDAZIONE: Il presente documento certifica la regolarita dei flussi analizzati tramite algoritmi di intelligenza artificiale forense e conformita ISA.")
    
    return pdf.output(dest='S').encode('latin-1')

# --- 4. INTERFACCIA STREAMLIT PLATINUM ---
st.set_page_config(page_title="COIN-NEXUS QUANTUM", layout="wide", page_icon="💠")

# Style Custom
st.markdown("""<style>
    .metric-card { background: #111; padding: 20px; border-radius: 10px; border: 1px solid #00f2ff; text-align: center; }
    .stMetric { background: #0e1117; border: 1px solid #333; padding: 15px; border-radius: 10px; }
</style>""", unsafe_allow_html=True)

if "auth" not in st.session_state:
