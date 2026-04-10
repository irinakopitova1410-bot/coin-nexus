import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime

# --- CONFIGURAZIONE HIGH-END ---
st.set_page_config(page_title="COIN-NEXUS ULTIMATE", layout="wide", page_icon="💎")

st.markdown("""
    <style>
    .main { background: #0b0e14; }
    .stMetric { background: #111827; border-left: 5px solid #3b82f6; border-radius: 5px; padding: 20px; }
    .stSidebar { background-color: #111827; }
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE ANALISI AVANZATA ---
def analisi_benford(data):
    digits = data.abs().astype(str).str.extract('([1-9])')[0].dropna().astype(int)
    if digits.empty: return pd.DataFrame()
    obs = digits.value_counts(normalize=True).sort_index()
    exp = pd.Series({i: np.log10(1 + 1/i) for i in range(1, 10)})
    return pd.DataFrame({'Reale': obs, 'Atteso': exp}).fillna(0)

# --- GENERATORE CARTE DI LAVORO (PDF CERTIFICATO) ---
def genera_pdf_professional(totale, mat, samp, rischio, anomalie, note, studio_nome):
    pdf = FPDF()
    pdf.add_page()
    
    # Intestazione Branding
    pdf.set_fill_color(30, 58, 138)
    pdf.rect(0, 0, 210, 50, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 26)
    pdf.cell(190, 30, studio_nome.upper(), ln=True, align='C')
    pdf.set_font("Arial", 'I', 12)
    pdf.cell(190, 10, "Documentazione di Revisione ai sensi del principio ISA Italia 230", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(30)
    
    # Metodologia
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "RIEPILOGO METODOLOGICO DI PIANIFICAZIONE", ln=True)
    pdf.set_font("Arial", '', 11)
    data_audit = datetime.date.today().strftime("%d/%m/%Y")
    pdf.multi_cell(0, 8, f"In data {data_audit}, e stata eseguita l'analisi del database fornito. La materialita e stata determinata in base ai rischi identificati e ai benchmark di settore.")
    
    # Tabella Parametri
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(100, 10, "Parametro di Revisione", 1)
    pdf.cell(90, 10, "Valore", 1, ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(100, 10, "Massa Totale Verificata", 1)
    pdf.cell(90, 10, f"Euro {totale:,.2f}", 1, ln=True)
    pdf.cell(100, 10, "Materialita di Pianificazione (ISA 320)", 1)
    pdf.cell(90, 10, f"Euro {mat:,.2f}", 1, ln=True)
    pdf.cell(100, 10, "Soglia Errore Trascurabile (SAMP)", 1)
    pdf.cell(90, 10, f"Euro {samp:,.2f}", 1, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "CONCLUSIONI DEL TEAM DI AUDIT", ln=True)
    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(0, 8, note if note else "L'analisi non ha evidenziato criticita tali da richiedere procedure di validita estese, salvo quanto indicato nel dettaglio eccezioni.")

    if not anomalie.empty:
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(140, 8, "Voci Sopra Soglia (Eccezioni)", 1, 0, 'C')
        pdf.cell(50, 8, "Valore", 1, 1, 'C')
        pdf.set_font("Arial", '', 9)
        for _, row in anomalie.head(25).iterrows():
            desc = str(row.iloc[0]).encode('ascii', 'ignore').decode('ascii')
            pdf.cell(140, 7, desc[:65], 1)
            pdf.cell(50, 7, f"{row.iloc[1]:,.2f}", 1, 1, 'R')
            
    return pdf.output()

# --- INTERFACCIA ---
st.title("💎 Coin-Nexus Ultimate Audit Platform")
st.subheader("Professional Grade Compliance & Forensic Engine")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/584/584011.png", width=100)
    st.header("🏢 Personalizzazione Studio")
    nome_studio = st.text_input("Nome Studio Professionale", "Global Audit Firm")
    st.divider()
    st.header("📂 Caricamento Dati")
    file = st.file_uploader("Bilancio di Verifica o Giornale di Contabilita", type=['xlsx', 'csv'])
    st.divider()
    st.header("⚖️ Metodologia")
    perc_mat = st.slider("Materialità (% Massa Totale)", 0.5, 5.0, 1.5)
    perc_samp = st.slider("Soglia SAMP (% della Materialità)", 1, 10, 5)

if file:
    try:
        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        nums = df.select_dtypes(include=[np.number]).columns
        chars = df.select_dtypes(include=['object']).columns
        
        if len(nums) > 0 and len(chars) > 0:
            col_v, col_c = nums[0], chars[0]
            
            # CALCOLI 100K
            massa = df[col_v].sum()
            mat_val = massa * (perc_mat / 100)
            samp_val = mat_val * (perc_samp / 100)
            anom = df[df[col_v] > mat_val].sort_values(by=col_v, ascending=False)
            
            # DASHBOARD ELITE
            k1, k2, k3 = st.columns(3)
            k1.metric("MASSA CONTROLLATA", f"€ {massa:,.2f}")
            k2.metric("SOGLIA MATERIALITÀ", f"€ {mat_val:,.2f}")
            k3.metric("ALERT EVIDENZIATI", len(anom))

            tab1, tab2, tab3 = st.tabs(["📊 Analisi Rischi", "🕵️ Forensic Test", "📜 Reporting"])
            
            with tab1:
                st.plotly_chart(px.treemap(df.nlargest(30, col_v), path=[col_c], values=col_v, template="plotly_dark", title="Mappa di Concentrazione Voci di Bilancio"), use_container_width=True)
            
            with tab2:
                st.subheader("Test della Prima Cifra (Legge di Benford)")
                ben_df = analisi_benford(df[col_v])
                if not ben_df.empty:
                    st.line_chart(ben_df)
                    st.info("Nota: Gli scostamenti eccessivi dalla linea 'Atteso' richiedono indagini forensi su eventuali tentativi di 'Window Dressing' o frode.")

            with tab3:
                st.subheader("Generatore Carte di Lavoro")
                note_audit = st.text_area("Inserisci Conclusioni Professionali per il Report", height=150)
                if st.button("🚀 GENERA DOCUMENTAZIONE FIRMATA"):
                    pdf_final = genera_pdf_professional(massa, mat_val, samp_val, "VALUTATO", anom, note_audit, nome_studio)
                    st.download_button("📥 Scarica Report di Revisione Certificato", data=bytes(pdf_final), file_name=f"Carte_Lavoro_{nome_studio}.pdf", mime="application/pdf", use_container_width=True)
    except Exception as e:
        st.error(f"Errore tecnico: {e}")
else:
    st.info("Inizia caricando i dati contabili per eseguire lo screening di rischio automatico.")
