import streamlit as st
import pandas as pd
import plotly.express as px

# 1. SETUP
st.set_page_config(page_title="COIN-NEXUS Audit", layout="wide")

# CSS per rendere l'app professionale
st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #e1e7ef; }
    .stMetric { background-color: #161e2d !important; border: 1px solid #1e293b; padding: 15px; border-radius: 10px; }
    div[data-testid="stExpander"] { background-color: #161e2d; border: none; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ COIN-NEXUS: AUDIT SYSTEM")
st.subheader("Analisi Solvibilità e Indicatori della Crisi")

# 2. CARICAMENTO FILE CON GESTIONE ERRORI BINARI
uploaded_file = st.file_uploader("Carica Bilancio (XLSX o CSV)", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        # Rilevamento automatico del formato
        if uploaded_file.name.lower().endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            try:
                df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='utf-8')
            except:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='latin1')

        # Pulizia nomi colonne
        df.columns = [str(c).strip() for c in df.columns]
        
        st.success(f"✅ File '{uploaded_file.name}' caricato con successo!")

        # 3. SELEZIONE COLONNE (Se il sistema non le trova da solo)
        col1, col2 = st.columns(2)
        
        default_cat = [c for c in df.columns if any(x in c.lower() for x in ['voce', 'descrizione', 'conto', 'categoria']) ]
        default_val = [c for c in df.columns if any(x in c.lower() for x in ['valore', 'importo', 'saldo', 'euro', 'totale']) ]

        with col1:
            c_col = st.selectbox("Seleziona colonna NOMI/VOCI:", df.columns, index=df.columns.get_loc(default_cat[0]) if default_cat else 0)
        with col2:
            v_col = st.selectbox("Seleziona colonna VALORI:", df.columns, index=df.columns.get_loc(default_val[0]) if default_val else 0)

        # 4. PULIZIA DATI NUMERICI
        df[v_col] = pd.to_numeric(df[v_col].astype(str).replace('[€, ]', '', regex=True), errors='coerce').fillna(0)

        # 5. CALCOLO INDICI REVISORI
        def get_total(keywords):
            pattern = '|'.join(keywords)
            return df[df[c_col].str.contains(pattern, na=False, case=False)][v_col].sum()

        att_corr = get_total(['attività correnti', 'attivo circolante', 'liquidità', 'rimanenze', 'crediti'])
        pass_corr = get_total(['passività correnti', 'debiti a breve', 'fornitori', 'banche'])
        patrimonio = get_total(['patrimonio netto', 'capitale sociale', 'riserve', 'utile'])
        debiti_tot = get_total(['passività', 'totale debiti', 'fondi', 'tfr'])

        # Calcolo Ratio
        liq_ratio = round(att_corr / pass_corr, 2) if pass_corr != 0 else 0
        solv_ratio = round(patrimonio / debiti_tot, 2) if debiti_tot != 0 else 0

        # 6. VISUALIZZAZIONE KPI
        m1, m2, m3 = st.columns(3)
        m1.metric("Indice Liquidità", liq_ratio, delta="Target > 1.2", delta_color="normal" if liq_ratio > 1.2 else "inverse")
        m2.metric("Solvibilità (D/E)", solv_ratio, delta="Solidità")
        m3.metric("Patrimonio Rilevato", f"€ {patrimonio:,.0f}")

        # 7. GRAFICO PROFESSIONALE
        st.markdown("---")
        df_plot = df[df[v_col] > 0].nlargest(10, v_col)
        fig = px.bar(df_plot, x=v_col, y=c_col, orientation='h', 
                     title="Top 10 Voci per
