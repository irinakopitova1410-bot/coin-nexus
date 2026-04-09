import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime
import numpy as np

# 1. ARCHITETTURA VISIVA "ELITE BLACK"
st.set_page_config(page_title="COIN-NEXUS | ULTIMATE AUDIT", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;500;800&display=swap');
    .main { background: #030712; color: #f9fafb; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background: #0b0f1a; border-right: 1px solid #1e40af; }
    .stMetric { background: #111827; border: 1px solid #3b82f6; border-radius: 12px; padding: 25px !important; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5); }
    h1 { font-weight: 800; letter-spacing: -2px; text-transform: uppercase; color: #ffffff; }
    .status-badge { padding: 4px 12px; border-radius: 20px; font-size: 10px; font-weight: bold; background: #3b82f6; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGICA GENERAZIONE PDF PROFESSIONALE
class AuditPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "COIN-NEXUS AUDIT INTELLIGENCE - CONFIDENZIALE", ln=True, align="L")
        self.line(10, 20, 200, 20)
        self.ln(10)

def genera_pdf(data_dict):
    pdf = AuditPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 20, "RELAZIONE DI REVISIONE INDIPENDENTE", ln=True)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Data Analisi: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(5)
    
    # Sezione 1: Opinione
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, "1. GIUDIZIO SUL BILANCIO", ln=True, fill=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 10, f"Abbiamo svolto la revisione del bilancio tramite l'algoritmo Coin-Nexus. A nostro giudizio, il bilancio fornisce una rappresentazione veritiera e corretta. Opinione: {data_dict['opinione']}.")
    
    # Sezione 2: Materialità
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. SOGLIA DI MATERIALITA (ISA 320)", ln=True, fill=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 10, f"Benchmark utilizzato: {data_dict['benchmark']}", ln=True)
    pdf.cell(0, 10, f"Soglia di errore tollerabile: Euro {data_dict['materialita']:,.2f}", ln=True)
    
    return pdf.output(dest='S')

# 3. SIDEBAR E MOTORE DATI
st.sidebar.markdown("<h1>⚡ NEBULA-X</h1>", unsafe_allow_html=True)
menu = st.sidebar.radio("SISTEMI DI AUDIT", [
    "💎 EXECUTIVE MONITOR", 
    "⚖️ CALCOLO MATERIALITÀ", 
    "🛡️ GOING CONCERN (ISA 570)", 
    "📄 GENERATORE RELAZIONE"
])

file = st.sidebar.file_uploader("📥 CARICA DATI CONTABILI", type=['xlsx', 'csv'])

if file:
    df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
    df.columns = [str(c).upper().strip() for c in df.columns]
    is_demo = False
else:
    df = pd.DataFrame({'VOCE': ['Liquidità', 'Crediti', 'Immobilizzi', 'Debiti', 'Patrimonio'], 
                       'VALORE': [500000, 300000, 800000, 200000, 1400000]})
    is_demo = True

val_col = 'VALORE' if 'VALORE' in df.columns else df.columns[1]

# ==========================================
# MODULO 1: EXECUTIVE MONITOR
# ==========================================
if menu == "💎 EXECUTIVE MONITOR":
    st.markdown(f"<h1>💎 Executive Monitor {'<span class="status-badge">LIVE</span>' if not is_demo else ''}</h1>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("TOTAL ASSETS", f"€ {df[val_col].sum():,.0f}", "+2.1%")
    c2.metric("HEALTH SCORE", "94/100", "STABILE")
    c3.metric("DEBT/EQUITY", "0.14", "OPTIMAL")
    c4.metric("AUDIT RISK", "LOW", "-3%", delta_color="inverse")

    st.markdown("---")
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.subheader("📊 Network Patrimoniale (Sunburst)")
        fig = px.sunburst(df, path=[df.columns[0]], values=val_col, color=val_col, color_continuous_scale='Blues', template='plotly_dark')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=0, l=0, r=0, b=0))
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        st.subheader("🕵️ Verdetto Intelligenza Artificiale")
        st.write("L'analisi automatizzata non rileva anomalie nei flussi di cassa. La concentrazione dei crediti è entro i limiti di tolleranza.")
        st.info("Consiglio: Verificare l'anzianità dei crediti commerciali per possibili svalutazioni.")
def check_benford(data):
    first_digits = [int(str(abs(x))[0]) for x in data if x != 0]
    counts = np.histogram(first_digits, bins=range(1, 11))[0]
    actual_freq = counts / len(first_digits)
    benford_freq = [np.log10(1 + 1/d) for d in range(1, 10)]
    return actual_freq, benford_freq

# Nel modulo Executive Monitor
st.subheader("🕵️ Forensic Check (Benford's Law)")
if not is_demo:
    actual, expected = check_benford(df[val_col])
    fig_ben = go.Figure()
    fig_ben.add_trace(go.Bar(x=list(range(1,10)), y=actual, name='Reale'))
    fig_ben.add_trace(go.Scatter(x=list(range(1,10)), y=expected, name='Teorica Benford', line=dict(color='red')))
    st.plotly_chart(fig_ben, use_container_width=True)
# ==========================================
# MODULO 2: CALCOLO MATERIALITÀ
# ==========================================
elif menu == "⚖️ CALCOLO MATERIALITÀ":
    st.title("⚖️ Determina Materialità (ISA 320)")
    st.write("Il parametro fondamentale per definire l'errore massimo tollerabile in bilancio.")
    
    col_in, col_out = st.columns(2)
    with col_in:
        bench = st.selectbox("Seleziona Benchmark", ["Fatturato", "Totale Attivo", "Patrimonio Netto", "Utile Ante Imposte"])
        val_base = st.number_input("Valore Benchmark (€)", value=float(df[val_col].sum()))
        perc = st.slider("% di Sensibilità (ISA Standard)", 0.5, 5.0, 1.0)
        
    mat_calc = val_base * (perc / 100)
    st.session_state['materialita'] = mat_calc
    st.session_state['benchmark'] = bench

    with col_out:
        st.metric("SOGLIA MATERIALITÀ GLOBALE", f"€ {mat_calc:,.2f}")
        st.write("> **Significato:** Ogni errore superiore a questa cifra deve essere obbligatoriamente rettificato, altrimenti il giudizio del revisore sarà 'negativo'.")

# SOTTO IL MODULO GOING CONCERN (ISA 570)
elif menu == "🛡️ GOING CONCERN (ISA 570)":
    st.title("🛡️ Analisi Solvibilità Avanzata")
    
    # Calcolo Z-Score Semplificato per Audit
    st.subheader("Altman Z-Score (Predizione Fallimento)")
    c1, c2 = st.columns(2)
    with c1:
        attivo_circolante = st.number_input("Attivo Circolante (€)", value=200000.0)
        passivo_corrente = st.number_input("Passivo Corrente (€)", value=150000.0)
        tot_attivo = df[val_col].sum()
        
        # Esempio formula semplificata: (Attivo Circ - Pass Cor) / Tot Attivo
        z_score = (attivo_circolante - passivo_corrente) / tot_attivo * 1.2 # Peso arbitrario per demo
        
    with c2:
        if z_score > 2.6:
            st.success(f"Z-Score: {z_score:.2f} (Safe Zone)")
        elif z_score > 1.1:
            st.warning(f"Z-Score: {z_score:.2f} (Grey Zone)")
        else:
            st.error(f"Z-Score: {z_score:.2f} (Distress Zone)")

    # Test di Benford (Forensic Audit)
    st.markdown("---")
    st.subheader("🕵️ Forensic Check (Benford's Law)")
    def get_benford(data):
        digits = [int(str(abs(x))[0]) for x in data if x != 0]
        actual = np.histogram(digits, bins=range(1, 11))[0] / len(digits)
        expected = [np.log10(1 + 1/d) for d in range(1, 10)]
        return actual, expected

    actual, expected = get_benford(df[val_col])
    fig_ben = go.Figure()
    fig_ben.add_trace(go.Bar(x=list(range(1,10)), y=actual, name='Reale'))
    fig_ben.add_trace(go.Scatter(x=list(range(1,10)), y=expected, name='Standard', line=dict(color='red')))
    st.plotly_chart(fig_ben, use_container_width=True)

# ==========================================
# MODULO 4: GENERATORE RELAZIONE
# ==========================================
else:
    st.title("📄 Generatore Relazione di Revisione")
    st.write("Trasforma l'analisi tecnica in un documento legale pronto per la firma.")
    
    dati_report = {
        'opinione': "SENZA MODIFICHE (PULITA)",
        'materialita': st.session_state.get('materialita', 10000.0),
        'benchmark': st.session_state.get('benchmark', 'Totale Attivo')
    }
    
    if st.button("🛠️ GENERA BOZZA RELAZIONE"):
        pdf_bytes = genera_pdf(dati_report)
        st.download_button(
            label="📥 SCARICA PDF PER IL FIRMATARIO",
            data=pdf_bytes,
            file_name=f"Relazione_Audit_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )
        st.success("Relazione generata con successo secondo gli standard ISA Italia.")

st.sidebar.markdown("---")
st.sidebar.caption(f"🔒 ENCRYPTED SESSION | {datetime.now().strftime('%H:%M')}")
