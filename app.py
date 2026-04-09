import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. SETUP PAGINA
st.set_page_config(page_title="COIN-NEXUS Intelligence", layout="wide")

# 2. DESIGN ELEGANTE (DARK MODE ELITE)
st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #e2e8f0; }
    .stMetric { background-color: #161e2d; padding: 15px; border-radius: 10px; border: 1px solid #1e293b; }
    .indicator-card {
        background-color: #161e2d; padding: 20px; border-radius: 12px;
        border-left: 5px solid #3b82f6; margin-bottom: 20px;
    }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ COIN-NEXUS: AUDIT INTELLIGENCE")
st.caption("Analisi Predittiva Solvibilità & Indicatori della Crisi d'Impresa")

# --- DASHBOARD STATICA (OPERATIVO) ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Esposizione Bancaria", "€ 412k", "-2%")
c2.metric("Rating Creditizio", "A+", "Stabile")
c3.metric("DSCR Stimato", "1.45", "Sicuro")
c4.metric("Allerta Revisori", "ZERO", "Ottimale", delta_color="normal")

st.markdown("---")

# --- CARICAMENTO DATI ---
st.subheader("📂 Caricamento Bilancio di Verifica")
file = st.file_uploader("Trascina qui il file (Excel/CSV)", type=['xlsx', 'csv'])

if file:
    try:
        # Lettura Intelligente
        if file.name.endswith('.csv'):
            df = pd.read_csv(file, sep=None, engine='python', on_bad_lines='skip')
        else:
            df = pd.read_excel(file)
            
        df.columns = df.columns.str.strip()
        
        # Identificazione Colonne
        cat_col = [c for c in df.columns if 'Categoria' in c or 'Voce' in c][0]
        val_col = [c for c in df.columns if 'Valore' in c or 'Importo' in c][0]
        
        # LOGICA REVISORI (Calcolo Indici)
        def get_v(name):
            return pd.to_numeric(df[df[cat_col].str.contains(name, na=False, case=False)][val_col], errors='coerce').sum()

        att_corr = get_v("Attività Correnti")
        pass_corr = get_v("Passività Correnti")
        patrimonio = get_v("Patrimonio Netto")
        debiti_tot = get_v("Passività")
        
        # CALCOLO INDICI CHIAVE
        liq_index = round(att_corr / pass_corr, 2) if pass_corr > 0 else 0
        solv_index = round(patrimonio / debiti_tot, 2) if debiti_tot > 0 else 0
        
        # COLORAZIONE RISCHIO
        risk_color = "#10b981" if liq_index > 1.1 else "#ef4444"
        risk_status = "STABILE" if liq_index > 1.1 else "SOTTO OSSERVAZIONE"

        # VISUALIZZAZIONE RISULTATI
        res1, res2, res3 = st.columns(3)
        with res1:
            st.markdown(f'<div class="indicator-card" style="border-left-color: {risk_color}"><h4>Indice Liquidità</h4><h2>{liq_index}</h2><p>Capacità di pagare i debiti a breve</p></div>', unsafe_allow_html=True)
        with res2:
            st.markdown(f'<div class="indicator-card" style="border-left-color: #3b82f6"><h4>Solvibilità Generale</h4><h2>{solv_index}</h2><p>Indice di indipendenza finanziaria</p></div>', unsafe_allow_html=True)
        with res3:
            st.markdown(f'<div class="indicator-card" style="border-left-color: {risk_color}"><h4>Stato Allerta</h4><h2>{risk_status}</h2><p>Protocollo Crisi d\'Impresa</p></div>', unsafe_allow_html=True)

        # GRAFICO PROFESSIONALE
        st.markdown("### 📊 Analisi Patrimoniale")
        fig = px.bar(df, x=cat_col, y=val_col, color=val_col, template="plotly_dark", color_continuous_scale="Blues")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Struttura file non riconosciuta. Errore: {e}")
else:
    st.info("👋 In attesa del bilancio. Carica un file per attivare l'analisi dei rischi.")
