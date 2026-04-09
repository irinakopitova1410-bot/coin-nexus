import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configurazione Base
st.set_page_config(page_title="COIN-NEXUS TITANIUM", layout="wide")

# CSS per evitare il caricamento bianco infinito
st.markdown("""<style>.main { background-color: #000; color: white; }</style>""", unsafe_allow_html=True)

# SIDEBAR
st.sidebar.title("⚡ NEBULA-X CORE")
menu = st.sidebar.radio("MODULI", ["💎 RIEPILOGO", "🕵️ RISCHIO", "📈 PROIEZIONI"])

# CARICAMENTO DATI
uploaded_file = st.sidebar.file_uploader("CARICA FILE", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
        st.success("Dati caricati con successo!")
    except Exception as e:
        st.error(f"Errore: {e}")
        df = pd.DataFrame({'VOCE': ['Esempio'], 'VALORE': [100]})
else:
    # DATI DI BACKUP PER FAR FUNZIONARE LA PAGINA SUBITO
    df = pd.DataFrame({'VOCE': ['Cassa', 'Crediti', 'Debiti'], 'VALORE': [50000, 30000, 20000]})

# VISUALIZZAZIONE MODULI
if menu == "💎 RIEPILOGO":
    st.title("💎 Riepilogo Esecutivo")
    c1, c2 = st.columns(2)
    c1.metric("TOTALE ATTIVO", f"€ {df.iloc[:, 1].sum():,.0f}")
    c2.metric("SALUTE AZIENDALE", "94/100")
    
    fig = px.pie(df, names=df.columns[0], values=df.columns[1], hole=0.4, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

elif menu == "🕵️ RISCHIO":
    st.title("🕵️ Analisi Rischio Big4")
    ir = st.slider("Rischio Intrinseco", 0.0, 1.0, 0.5)
    cr = st.slider("Rischio di Controllo", 0.0, 1.0, 0.3)
    st.write(f"### Rischio Totale: {round(ir * cr * 100, 2)}%")

else:
    st.title("📈 Proiezioni")
    fig = px.line(x=[1,2,3,4,5], y=[10,15,13,18,20], title="Trend Previsto")
    st.plotly_chart(fig, use_container_width=True)
    elif menu == "💎 MATERIALITÀ (ISA 320)":
    st.title("💎 Calcolo della Materialità Professionale")
    benchmark = st.selectbox("Seleziona Benchmark", ["Fatturato", "Totale Attivo", "Utile Ante Imposte"])
    valore_base = st.number_input(f"Inserisci Valore {benchmark}", value=1000000)
    
    perc = st.slider("% di Sensibilità", 0.5, 5.0, 1.0)
    mat_globale = valore_base * (perc / 100)
    
    st.metric("Materialità Globale (Overall Materiality)", f"€ {mat_globale:,.0f}")
    st.info(f"Ogni errore superiore a € {mat_globale:,.0f} richiede una rettifica obbligatoria del bilancio.")
