import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAZIONE
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

# --- CARICAMENTO ---
file = st.file_uploader("Carica il tuo file Excel del Bilancio", type=['xlsx', 'csv'])

if file:
    try:
        # Lettura file
        if file.name.endswith('xlsx'):
            df = pd.read_excel(file)
        else:
            df = pd.read_csv(file, sep=None, engine='python', on_bad_lines='skip')
        
        # Pulizia automatica nomi colonne
        df.columns = df.columns.str.strip()
        
        # Tenta di trovare le colonne Categoria e Valore
        cat_cols = [c for c in df.columns if any(x in c.lower() for x in ['cat', 'voce', 'descrizione', 'conto'])]
        val_cols = [c for c in df.columns if any(x in c.lower() for x in ['valore', 'importo', 'euro', 'saldo', 'dare', 'avere'])]

        if not cat_cols or not val_cols:
            st.error("❌ Non trovo le colonne 'Voce' e 'Valore'. Controlla l'intestazione del tuo Excel.")
            st.write("Colonne trovate nel tuo file:", list(df.columns))
        else:
            c_col = cat_cols[0]
            v_col = val_cols[0]

            # Pulizia Numeri (rimuove simboli valuta e trasforma in numeri veri)
            df[v_col] = pd.to_numeric(df[v_col].astype(str).replace('[€, ]', '', regex=True), errors='coerce').fillna(0)

            # FUNZIONE DI RICERCA AGGRESSIVA
            def somma_voci(keywords):
                pattern = '|'.join(keywords)
                return df[df[c_col].str.contains(pattern, na=False, case=False)][v_col].sum()

            # Calcolo Indici con termini comuni nei bilanci italiani
            attivo = somma_voci(['attività correnti', 'attivo circolante', 'rimanenze', 'liquidità', 'crediti'])
            passivo = somma_voci(['passività correnti', 'debiti a breve', 'debiti verso fornitori', 'banche c/c'])
            capitale = somma_voci(['patrimonio netto', 'capitale sociale', 'riserve', 'utile'])
            debiti_t = somma_voci(['passività', 'totale debiti', 'fondi rischi', 'tfr'])

            # Calcolo Indici
            liq = round(attivo / passivo, 2) if passivo > 0 else 0
            solv = round(capitale / debiti_t, 2) if debiti_t > 0 else 0
            
            # --- INTERFACCIA RISULTATI ---
            col1, col2, col3 = st.columns(3)
            
            with col1:
                colore = "#10b981" if liq > 1.2 else "#ef4444"
                st.markdown(f'<div class="indicator-card" style="border-left-color: {colore}"><h4>Indice Liquidità</h4><h2>{liq}</h2><p>Target: > 1.2</p></div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown(f'<div class="indicator-card" style="border-left-color: #3b82f6"><h4>Solvibilità</h4><h2>{solv}</h2><p>Indipendenza Finanziaria</p></div>', unsafe_allow_html=True)
                
            with col3:
                st.markdown(f'<div class="indicator-card"><h4>Patrimonio Netto</h4><h2>€ {capitale:,.2f}</h2><p>Solidità rilevata</p></div>', unsafe_allow_html=True)

            # --- DEBUG TABLE (Solo se i valori sono zero) ---
            if attivo == 0 or passivo == 0:
                st.warning("⚠️ Attenzione: Sto leggendo 0 in alcune voci. Controlla se i nomi nel tuo Excel corrispondono.")
                with st.expander("Vedi i dati che sto leggendo"):
                    st.dataframe(df[[c_col, v_col]])

            # --- GRAFICO ---
            st.markdown("### 📊 Analisi Grafica Voci Maggiori")
            df_graph = df[df[v_col] > 0].nlargest(10, v_col)
            fig = px.pie(df_graph, names=c_col, values=v_col, hole=0.4, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"💥 Errore Critico: {e}")
