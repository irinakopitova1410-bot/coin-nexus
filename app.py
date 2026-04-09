import streamlit as st
import pandas as pd
import plotly.express as px

# 1. SETUP ESTETICO
st.set_page_config(page_title="COIN-NEXUS Intelligence", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #e2e8f0; }
    .indicator-card {
        background-color: #161e2d; padding: 20px; border-radius: 12px;
        border-left: 5px solid #3b82f6; margin-bottom: 20px; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ COIN-NEXUS: AUDIT INTELLIGENCE")
st.info("💡 Assicurati che il tuo Excel abbia una colonna 'Categoria' (o 'Voce') e una 'Valore' (o 'Importo').")

# --- CARICAMENTO ---
file = st.file_uploader("Carica Bilancio (Excel/CSV)", type=['xlsx', 'csv'])

if file:
    try:
        # Lettura file
        df = pd.read_excel(file) if file.name.endswith('xlsx') else pd.read_csv(file, sep=None, engine='python')
        
        # Pulizia colonne
        df.columns = df.columns.str.strip()
        
        # Trova le colonne giuste in automatico
        cat_col = [c for c in df.columns if any(x in c.lower() for x in ['cat', 'voce', 'descrizione'])][0]
        val_col = [c for c in df.columns if any(x in c.lower() for x in ['valore', 'importo', 'euro'])][0]
        
        # Forza i numeri (toglie simboli € o spazi)
        df[val_col] = pd.to_numeric(df[val_col].replace('[€, ]', '', regex=True), errors='coerce').fillna(0)

        # LOGICA DI RICERCA FLESSIBILE (Sostituisci i nomi con quelli del TUO Excel se diversi)
        def get_v(keywords):
            # Cerca righe che contengono ALMENO UNA delle parole chiave
            mask = df[cat_col].str.contains('|'.join(keywords), na=False, case=False)
            return df[mask][val_col].sum()

        # Definiamo cosa cercare (Aggiungi qui i nomi esatti che usi nel tuo Excel)
        a_c = get_v(['attività correnti', 'attivo circolante', 'disponibilità'])
        p_c = get_v(['passività correnti', 'debiti a breve', 'scadenze brevi'])
        pat = get_v(['patrimonio netto', 'capitale sociale', 'riserve'])
        p_t = get_v(['passività', 'totale debiti', 'debiti totali'])

        # Calcolo Indici
        liq = round(a_c / p_c, 2) if p_c > 0 else 0
        solv = round(pat / p_t, 2) if p_t > 0 else 0
        
        color_liq = "#10b981" if liq > 1.2 else "#fbbf24" if liq > 0.8 else "#ef4444"
        
        # CARD RISULTATI
        res1, res2, res3 = st.columns(3)
        with res1:
            st.markdown(f'<div class="indicator-card" style="border-left-color: {color_liq}"><h4>Liquidità Corrente</h4><h2>{liq}</h2><p>Target > 1.2</p></div>', unsafe_allow_html=True)
        with res2:
            st.markdown(f'<div class="indicator-card" style="border-left-color: #3b82f6"><h4>Solvibilità</h4><h2>{solv}</h2><p>Indipendenza Finanziaria</p></div>', unsafe_allow_html=True)
        with res3:
            st.markdown(f'<div class="indicator-card"><h4>Patrimonio Rilevato</h4><h2>€ {pat:,.0f}</h2><p>Solidità interna</p></div>', unsafe_allow_html=True)

        # GRAFICO
        st.markdown("### 📊 Analisi Voci di Bilancio")
        df_plot = df[df[val_col] != 0].nlargest(12, val_col)
        fig = px.bar(df_plot, x=cat_col, y=val_col, color=val_col, template="plotly_dark", color_continuous_scale="Viridis")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Errore: {e}. Cont
