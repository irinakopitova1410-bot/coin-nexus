import streamlit as st
import pandas as pd
import plotly.express as px

# 1. SETUP INTERFACCIA ELITE
st.set_page_config(page_title="Coin-Nexus Audit", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #e2e8f0; }
    .stMetric { background-color: #161e2d !important; border: 1px solid #1e293b; padding: 20px; border-radius: 12px; }
    .audit-card {
        background-color: #161e2d; padding: 20px; border-radius: 12px;
        border-left: 5px solid #3b82f6; margin-bottom: 20px;
    }
    .status-ok { color: #10b981; font-weight: bold; }
    .status-risk { color: #ef4444; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ COIN-NEXUS: AUDIT & REVISIONE")
st.caption("Sistema Integrato di Analisi Solvibilità e Indicatori della Crisi d'Impresa")

# --- CARICAMENTO ---
uploaded_file = st.file_uploader("Trascina qui il Bilancio di Verifica (Excel o CSV)", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        # Lettura Intelligente
        if uploaded_file.name.lower().endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='latin1')
        
        df.columns = [str(c).strip() for c in df.columns]
        
        # Identificazione Automatica Colonne
        c_col = [c for c in df.columns if any(x in c.lower() for x in ['voce', 'descrizione', 'conto', 'categoria'])][0]
        v_col = [c for c in df.columns if any(x in c.lower() for x in ['valore', 'importo', 'saldo', 'fine'])][0]
        
        # Pulizia Valori
        df[v_col] = pd.to_numeric(df[v_col].astype(str).replace('[€, ]', '', regex=True), errors='coerce').fillna(0)

        # --- LOGICA DEL REVISORE (Mapping termini di bilancio) ---
        def audit_sum(keywords):
            pattern = '|'.join(keywords)
            return df[df[c_col].str.contains(pattern, na=False, case=False)][v_col].sum()

        # Estrazione Masse Patrimoniali
        liquidita = audit_sum(['cassa', 'banca', 'disponibilità liquide', 'tesoreria'])
        crediti_breve = audit_sum(['clienti', 'crediti v/clienti', 'crediti commerciali'])
        rimanenze = audit_sum(['rimanenze', 'magazzino', 'scorte'])
        attivo_corr = liquidita + crediti_breve + rimanenze
        
        debiti_breve = audit_sum(['fornitori', 'banche c/c', 'debiti tributari', 'debiti commerciali', 'passività correnti'])
        patrimonio = audit_sum(['patrimonio netto', 'capitale sociale', 'riserve', 'utile d\'esercizio'])
        debiti_tot = audit_sum(['passività', 'totale debiti', 'tfr', 'mutui', 'fondi rischi'])

        # --- CALCOLO INDICI REVISIONE ---
        # 1. Indice di Liquidità (Current Ratio)
        liq_index = round(attivo_corr / debiti_breve, 2) if debiti_breve != 0 else 0
        
        # 2. Indice di Solvibilità (Autonomia Finanziaria)
        solv_index = round(patrimonio / (patrimonio + debiti_tot), 2) if (patrimonio + debiti_tot) != 0 else 0
        
        # --- VISUALIZZAZIONE KPI ---
        k1, k2, k3 = st.columns(3)
        
        status_liq = "✅ OTTIMALE" if liq_index > 1.2 else "⚠️ TENSIONE" if liq_index > 1 else "🚨 CRITICO"
        k1.metric("Liquidità Corrente", liq_index, status_liq)
        
        status_solv = "✅ SOLIDO" if solv_index > 0.3 else "⚠️ LEVERAGE ALTO"
        k2.metric("Indipendenza Fin.", f"{solv_index*100:.1f}%", status_solv)
        
        k3.metric("Patrimonio Netto", f"€ {patrimonio:,.0f}")

        st.markdown("---")

        # --- SEZIONE REVISORE: VERDETTO ---
        col_a, col_b = st.columns([1, 2])
        
        with col_a:
            st.subheader("🕵️ Verdetto Revisore")
            if liq_index < 1:
                st.error("ATTENZIONE: Squilibrio finanziario rilevato. Le passività a breve termine superano le attività liquide.")
            elif solv_index < 0.1:
                st.warning("RISCHIO: Sottopatrimonializzazione. L'azienda dipende troppo da capitali esterni.")
            else:
                st.success("STABILITÀ: Non si rilevano segnali di allerta ai sensi del Codice della Crisi.")

        with col_b:
            st.subheader("📊 Composizione Attivo Circolante")
            fig_data = pd.DataFrame({
                'Voce': ['Liquidità', 'Crediti', 'Rimanenze'],
                'Valore': [liquidita, crediti_breve, rimanenze]
            })
            fig = px.donut(fig_data, names='Voce', values='Valore', hole=0.4, 
                           color_discrete_sequence=px.colors.sequential.Blues_r,
                           template="plotly_dark")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)

        # Tabella di Analisi per controllo umano
        with st.expander("🔍 Esamina Bilancio di Verifica Completo"):
            st.dataframe(df[[c_col, v_col]], use_container_width=True)

    except Exception as e:
        st.error(f"Errore di lettura: {e}")
        st.info("Assicurati che il file abbia una colonna 'Descrizione' e una colonna 'Saldo' o 'Valore'.")

else:
    st.info("👋 In attesa del caricamento del Bilancio di Verifica per l'Audit.")
