import streamlit as st
import pandas as pd
import plotly.express as px

# 1. DESIGN & INTERFACCIA
st.set_page_config(page_title="Coin-Nexus Audit", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #e2e8f0; }
    .stMetric { background-color: #161e2d !important; border: 1px solid #1e293b; padding: 20px; border-radius: 12px; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ COIN-NEXUS: AUDIT INTELLIGENCE")
st.caption("Analisi Solvibilità & Indicatori della Crisi d'Impresa (CCII)")

# --- CARICAMENTO ---
uploaded_file = st.file_uploader("📂 Carica Bilancio (XLSX o CSV)", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        # Lettura automatica
        if uploaded_file.name.lower().endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='latin1')
        
        # Pulizia colonne
        df.columns = [str(c).strip() for c in df.columns]
        
        # Identificazione Colonne
        c_col = [c for c in df.columns if any(x in c.lower() for x in ['voce', 'desc', 'conto', 'cat'])][0]
        v_col = [c for c in df.columns if any(x in c.lower() for x in ['valore', 'importo', 'saldo', 'euro'])][0]
        
        # Pulizia Valori Numerici
        df[v_col] = pd.to_numeric(df[v_col].astype(str).replace('[€, ]', '', regex=True), errors='coerce').fillna(0)

        # --- LOGICA DEL REVISORE ---
        def get_v(keywords):
            mask = df[c_col].str.contains('|'.join(keywords), na=False, case=False)
            return df[mask][v_col].sum()

        liquidita = get_v(['cassa', 'banca', 'disponibilità'])
        crediti = get_v(['clienti', 'crediti v/clienti'])
        magazzino = get_v(['rimanenze', 'magazzino', 'scorte'])
        passivo_breve = get_v(['fornitori', 'banche c/c', 'debiti tributari', 'debiti a breve'])
        patrimonio = get_v(['patrimonio netto', 'capitale sociale', 'riserve', 'utile'])
        debiti_tot = get_v(['passività', 'totale debiti', 'mutui', 'tfr'])

        # --- INDICI CHIAVE ---
        liq_index = round((liquidita + crediti + magazzino) / passivo_breve, 2) if passivo_breve > 0 else 0
        solv_index = round(patrimonio / (patrimonio + debiti_tot), 2) if (patrimonio + debiti_tot) > 0 else 0

        # --- DASHBOARD KPI ---
        k1, k2, k3 = st.columns(3)
        
        status_l = "✅ OK" if liq_index > 1.2 else "⚠️ TENSIONE" if liq_index > 1 else "🚨 ALLERTA"
        k1.metric("Indice Liquidità", liq_index, status_l)
        
        status_s = "✅ SOLIDO" if solv_index > 0.25 else "⚠️ DEBOLE"
        k2.metric("Solvibilità", f"{solv_index*100:.1f}%", status_s)
        
        k3.metric("Patrimonio Netto", f"€ {patrimonio:,.0f}")

        st.markdown("---")

        # --- ANALISI VISIVA & VERDETTO ---
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            st.subheader("🕵️ Verdetto Revisione")
            if liq_index < 1:
                st.error("🚨 SQUILIBRIO RILEVATO: Rischio crisi imminente (Le passività superano le attività correnti).")
            elif solv_index < 0.15:
                st.warning("⚠️ STRUTTURA DEBOLE: L'azienda è eccessivamente indebitata rispetto ai mezzi propri.")
            else:
                st.success("✅ EQUILIBRIO: Gli indicatori non mostrano segnali di crisi immediata.")

        with col_right:
            st.subheader("📊 Analisi Asset Correnti")
            asset_data = pd.DataFrame({
                'Voce': ['Liquidità', 'Crediti', 'Magazzino'],
                'Valore': [liquidita, crediti, magazzino]
            })
            # Completamento del grafico e chiusura funzione
            fig = px.pie(asset_data, names='Voce', values='Valore', hole=0.5, 
                         template="plotly_dark", 
                         color_discrete_sequence=px.colors.sequential.Blues_r)
            
            fig.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Errore tecnico: {e}")
        st.info("Assicurati che il file caricato contenga le colonne 'Descrizione' e 'Saldo'.")
else:
    st.info("👋 In attesa del caricamento del Bilancio per l'Audit.")
