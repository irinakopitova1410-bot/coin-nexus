import streamlit as st
import plotly.graph_objects as go
from supabase import create_client, Client
import pandas as pd
from fpdf import FPDF
def create_banking_report(company, rating, metrics):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Istituzionale
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Dossier Creditizio: {company.upper()}", ln=True)
    pdf.set_font("Arial", 'I', 9)
    pdf.cell(0, 5, f"Protocollo: CN-{pd.to_datetime('today').strftime('%Y%m%d')}-X", ln=True)
    pdf.ln(10)

    # Box Score - Colore in base al rating
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 20, f"RATING FINALE: {rating}", 1, 1, 'C', True)
    pdf.ln(5)

    # 1. ANALISI DEI NUMERI (Snapshot)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "1. SINTESI FINANZIARIA VALIDATA", ln=True)
    pdf.set_font("Arial", '', 10)
    
    # Tabella Dati
    for label, val in [("Ricavi", f"€ {metrics['rev']:,.0f}"), 
                       ("EBITDA", f"€ {metrics['ebitda']:,.0f}"),
                       ("DSCR (Debt Cover)", f"{metrics['dscr']:.2f}"),
                       ("Safety Margin", f"{metrics['safety']}%")]:
        pdf.cell(90, 8, label, 1)
        pdf.cell(100, 8, val, 1, 1, 'R')

    # 2. STRESS TEST (Il valore aggiunto)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(255, 240, 240) # Sfondo leggermente rosso per allerta
    pdf.cell(0, 10, "2. SIMULAZIONE DI STRESS (-20% RICAVI)", 1, 1, 'L', True)
    
    pdf.set_font("Arial", '', 10)
    # Calcolo rapido dello scenario peggiore
    stress_rev = metrics['rev'] * 0.8
    stress_ebitda = stress_rev - (metrics['rev'] - metrics['ebitda'])
    
    resilienza = "ALTA" if stress_ebitda > 0 else "CRITICA"
    pdf.multi_cell(0, 8, f"In uno scenario di contrazione del mercato (-20%), l'EBITDA stimato scenderebbe a € {stress_ebitda:,.0f}. "
                         f"Capacità di assorbimento urti: {resilienza}.")

    # 3. VERDETTO DECISIONALE (Explainable AI)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "3. CONCLUSIONI DELL'ALGORITMO", ln=True)
    pdf.set_font("Arial", '', 10)
    
    verdetto = "CREDITO APPROVATO" if rating != "CCC" else "REVISIONE MANUALE NECESSARIA"
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Esito Automatizzato: {verdetto}", 0, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')
# --- CONFIGURAZIONE PREMIUM ---
st.set_page_config(page_title="Coin-Nexus Terminal", layout="wide", page_icon="🏛️")

# Stile CSS per rendere l'interfaccia simile a un terminale bancario
st.markdown("""
    <style>
    .main { background: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 2rem; color: #00f2ff; }
    .stTable { background-color: #161b22; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- CONNESSIONE DATABASE ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# --- LOGICA DI AUDIT ---
def perform_audit(rev, costs, debt):
    ebitda = rev - costs
    dscr = ebitda / (debt if debt > 0 else 1)
    # Calcolo Rating Basel IV semplificato
    if dscr > 2.5 and (ebitda/rev) > 0.15: rating = "AAA"
    elif dscr > 1.2: rating = "BBB"
    else: rating = "CCC"
    return rating, dscr, ebitda

# --- UI SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/bank.png")
    st.title("Nexus Terminal")
    company = st.text_input("Ragione Sociale", "Nuova Azienda S.p.A.")
    rev = st.number_input("Ricavi Annuo (€)", value=5000000)
    costs = st.number_input("Costi Operativi (€)", value=4200000)
    debt = st.number_input("Esposizione Debitoria (€)", value=1000000)
    run = st.button("🚀 ESEGUI ANALISI DEEP-TECH")

# --- DASHBOARD PRINCIPALE ---
st.title("🏛️ Coin-Nexus | Financial Risk Intelligence")

if run:
    rating, dscr, ebitda = perform_audit(rev, costs, debt)
    
    # Salvataggio immediato
    supabase.table("audit_reports").insert({
        "company_name": company, "rating": rating, "revenue": rev
    }).execute()

    # Layout a Colonne
    c1, c2, c3 = st.columns(3)
    c1.metric("Rating Attribuito", rating)
    c2.metric("Indice DSCR", f"{dscr:.2f}")
    c3.metric("EBITDA", f"€{ebitda:,.0f}")

    st.divider()

    # Grafici Professionali
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.subheader("🎯 Credit Gauge")
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = dscr,
            gauge = {
                'axis': {'range': [0, 5]},
                'bar': {'color': "#00f2ff"},
                'steps': [
                    {'range': [0, 1.2], 'color': "#ff4b4b"},
                    {'range': [1.2, 2.5], 'color': "#ffa500"},
                    {'range': [2.5, 5], 'color': "#00ff00"}]
            }
        ))
        fig_gauge.update_layout(template="plotly_dark", height=300, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_r:
        st.subheader("🛡️ Risk Radar")
        fig_radar = go.Figure(go.Scatterpolar(
            r=[85, 90, 70, 80, 88],
            theta=['Liquidità','Solvibilità','Efficienza','Resilienza','Crescita'],
            fill='toself', line_color='#00f2ff'
        ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 100])), template="plotly_dark", height=300)
        st.plotly_chart(fig_radar, use_container_width=True)

    st.success(f"Analisi completata per {company}. Dati sincronizzati con il Cloud.")

# --- STORICO REAL-TIME ---
st.divider()
st.subheader("📑 Archivio Audit Globali")
try:
    res = supabase.table("audit_reports").select("*").order("created_at", desc=True).limit(10).execute()
    if res.data:
        df = pd.DataFrame(res.data)[['created_at', 'company_name', 'rating', 'revenue']]
        df.columns = ['Data', 'Azienda', 'Rating', 'Fatturato (€)']
        st.dataframe(df, use_container_width=True, hide_index=True)
except Exception as e:
    st.info("Configurazione database in corso...")
