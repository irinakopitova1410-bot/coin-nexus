
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime
import numpy as np

# --- 1. SETUP & SESSION ---
st.set_page_config(page_title="COIN-NEXUS ULTIMATE", layout="wide")

if 'mat' not in st.session_state: st.session_state['mat'] = 15000.0
if 'dscr' not in st.session_state: st.session_state['dscr'] = 1.4

# --- 2. LOGICA CARICAMENTO ---
st.sidebar.title("💠 COIN-NEXUS CORE")
uploaded_file = st.sidebar.file_uploader("📥 CARICA BILANCIO (XLSX o CSV)", type=['xlsx', 'csv'])

def load_data(file):
    try:
        if file.name.endswith('.xlsx'):
            temp_df = pd.read_excel(file, engine='openpyxl')
        else:
            temp_df = pd.read_csv(file, sep=None, engine='python')
        
        temp_df.columns = [str(c).upper().strip() for c in temp_df.columns]
        n_cols = temp_df.select_dtypes(include=[np.number]).columns.tolist()
        t_cols = temp_df.select_dtypes(include=[object]).columns.tolist()
        
        if n_cols and t_cols:
            return temp_df[[t_cols[0], n_cols[0]]], t_cols[0], n_cols[0]
        return None, None, None
    except Exception as e:
        return None, None, None

if uploaded_file:
    df, lab_col, val_col = load_data(uploaded_file)
    if df is None:
        df = pd.DataFrame({'VOCE': ['Cassa', 'Debiti'], 'VALORE': [500000, 200000]})
        lab_col, val_col = 'VOCE', 'VALORE'
else:
    df = pd.DataFrame({'VOCE': ['Cassa', 'Crediti', 'Debiti', 'Patrimonio'], 'VALORE': [400000, 300000, 200000, 500000]})
    lab_col, val_col = 'VOCE', 'VALORE'

# --- 3. MENU ---
menu = st.sidebar.radio("SISTEMI", ["📊 DASHBOARD", "🛡️ GOING CONCERN", "🕵️ FORENSIC", "📄 REPORT PDF"])

if menu == "📊 DASHBOARD":
    st.title("📊 Financial Intelligence")
    c1, c2 = st.columns(2)
    c1.metric("TOTAL ASSETS", f"€ {df[val_col].sum():,.0f}")
    c2.metric("DATA STATUS", "FILE OK" if uploaded_file else "DEMO MODE")
    fig = px.sunburst(df, path=[lab_col], values=val_col, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

elif menu == "🛡️ GOING CONCERN":
    st.title("🛡️ Verifica Continuità (ISA 570)")
    st.session_state['dscr'] = st.slider("Indice DSCR", 0.5, 3.0, float(st.session_state['dscr']))
    
    # Radar Chart corretto (Syntax Fix)
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[5, 4, 3, 5, 4],
        theta=['Liquidità', 'Solvibilità', 'Redditività', 'Efficienza', 'Patrimonio'],
        fill='toself',
        name='Rating'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

elif menu == "🕵️ FORENSIC":
    st.title("🕵️ Forensic Audit (Benford's Law)")
    digits = [int(str(abs(x))[0]) for x in df[val_col] if x != 0]
    if digits:
        actual = np.histogram(digits, bins=range(1, 11))[0] / len(digits)
        expected = [np.log10(1 + 1/d) for d in range(1, 10)]
        fig_b = go.Figure()
        fig_b.add_trace(go.Bar(x=list(range(1,10)), y=actual, name='Reale'))
        fig_b.add_trace(go.Scatter(x=list(range(1,10)), y=expected, name='Benford', line=dict(color='red')))
        fig_b.update_layout(template="plotly_dark")
        st.plotly_chart(fig_b, use_container_width=True)

else:
    st.title("📄 Report PDF")
    if st.button("🛠️ GENERA DOCUMENTO"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "RELAZIONE DI REVISIONE COIN-NEXUS", ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Materialita: Euro {st.session_state['mat']:
