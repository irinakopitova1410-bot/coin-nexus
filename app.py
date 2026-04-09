import streamlit as st
import pandas as pd
import plotly.express as px

# 1. SETUP
st.set_page_config(page_title="COIN-NEXUS Intelligence", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #e2e8f0; }
    .indicator-card {
        background-color: #161e2d; padding: 20px; border-radius: 12px;
        border-left: 5px solid #3b82f6; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ COIN-NEXUS: AUDIT INTELLIGENCE")

# --- CARICAMENTO ---
file = st.file_uploader("Carica Bilancio (Excel/CSV)", type=['xlsx', 'csv'])

if file:
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file, sep=None, engine='python', on_bad_lines='skip')
        else:
            df = pd.read_excel(file)
            
        df.columns = df.columns.str.strip()
        
        # PULIZIA DATI (Risolve l'errore Timedelta/JSON)
        # Trasformiamo tutto ciò che non è testo o numero in stringa o lo rimuoviamo
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]) or pd.api.types.is_timedelta64_dtype(df[col]):
                df[col] = df[col].astype(str)

        cat_col = [c for c in df.columns if 'Categoria' in c or 'Voce' in c][0]
        val_col = [c for c in df.columns if 'Valore' in c or 'Importo' in c][0]
        
        # Assicuriamoci che la colonna Valore sia numerica
        df[val_col] = pd.to_numeric(df[val_col], errors='coerce').fillna(0)

        # LOGICA REVISORI
        def get_v(name):
            return df[df[cat_col].str.contains(name, na=False, case=False)][val_col].sum()

        a_c, p_c, pat, p_t = get_v("Attività Correnti"), get_v("Passività Correnti"), get_v("Patrimonio Netto"), get_v("Passività")
        
        liq = round(a_c / p_c, 2) if p_c > 0 else 0
        solv = round(pat / p_t, 2) if p_t > 0 else 0
        
        color = "#10b981" if liq > 1.1 else "#ef4444"
        
        # CARD
        res1, res2 = st.columns(2)
        res1.markdown(f'<div class="indicator-card" style="border-left-color: {color}"><h4>Liquidità</h4><h2>{liq}</h2></div>', unsafe_allow_html=True)
        res2.markdown(f'<div class="indicator-card"><h4>Solvibilità</h4><h2>{solv}</h2></div>', unsafe_allow_html=True)

        # GRAFICO (Senza errori di serializzazione)
        st.markdown("### 📊 Analisi Patrimoniale")
        # Prendiamo solo le prime 15 voci per non affollare
        df_plot = df.nlargest(15, val_col) 
        fig = px.bar(df_plot, x=cat_col, y=val_col, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Errore tecnico: {e}. Controlla che le colonne si chiamino 'Categoria' e 'Valore'.")
