import streamlit as st
import requests
import time
import pandas as pd
from supabase import create_client

# Configurazione Pagina
st.set_page_config(page_title="Nexus Pro AI", layout="wide", page_icon="📊")

# Inizializzazione Supabase (Assicurati che i Secrets siano impostati su Streamlit Cloud)
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception as e:
    st.error("Errore di configurazione Secrets: Controlla SUPABASE_URL e SUPABASE_KEY")

# Endpoint del tuo Backend su Render
API_URL = "https://finance-analyzer-q9m8.onrender.com/v1/analyze"
API_KEY = "nx-live-docfinance-2026"

st.title("🏛️ Nexus Finance AI - Analisi Avanzata")
st.markdown("Analisi andamento, EBITDA, Altman Z-Score e Proiezioni Future.")

# Sidebar per info aziendali
st.sidebar.header("Dati Azienda")
azienda = st.sidebar.text_input("Ragione Sociale", placeholder="Es. DocFinance S.p.A.")
st.sidebar.markdown("---")

# Caricamento File
uploaded_file = st.file_uploader("Carica Bilancio Excel (.xlsx)", type=["xlsx"])

if uploaded_file and azienda:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("File caricato correttamente!")
        
        with st.expander("Visualizza Anteprima Dati"):
            st.dataframe(df.head())

        if st.button("🚀 ESEGUI ANALISI COMPLETA"):
            # Preparazione dati per il backend
            records = df.to_dict(orient="records")
            payload = {
                "azienda": azienda,
                "records": records
            }
            headers = {"x-api-key": API_KEY}
            
            with st.status("L'IA sta elaborando i dati finanziari...", expanded=True) as status:
                try:
                    # Chiamata al Backend
                    response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
                    
                    if response.status_code == 200:
                        analysis_id = response.json().get("id")
                        status.update(label="✅ Dati ricevuti! Calcolo indicatori in corso...", state="running")
                        
                        # Polling Supabase per i risultati
                        completato = False
                        for i in range(15): # Massimo 75 secondi di attesa
                            time.sleep(5)
                            res = supabase.table("analisi_rischio").select("*").eq("id", analysis_id).execute()
                            
                            if res.data and res.data[0].get('completato'):
                                data = res.data[0]
                                status.update(label="✨ Analisi Ultimata!", state="complete")
                                st.balloons()
                                
                                # Dashboard Risultati
                                st.divider()
                                c1, c2, c3 = st.columns(3)
                                c1.metric("Altman Z-Score", data.get('z_score', 'N/D'))
                                c2.metric("EBITDA Stimato", f"€ {data.get('ebitda', 0):,.2f}")
                                c3.info(f"Stato: {data.get('stato_rischio', 'In analisi')}")
                                
                                # Grafico Proiezioni
                                if data.get('proiezioni'):
                                    st.subheader("📈 Proiezione Andamento (Prossimi 4 Anni)")
                                    st.line_chart(data['proiezioni'])
                                
                                completato = True
                                break
                        
                        if not completato:
                            st.warning("Il calcolo sta richiedendo tempo. I risultati appariranno a breve su Supabase.")
                    else:
                        st.error(f"Errore Backend: {response.status_code}")
                except Exception as e:
                    st.error(f"Errore di connessione: {str(e)}")

    except Exception as e:
        st.error(f"Errore nella lettura dell'Excel: {e}")
else:
    st.info("Inserisci il nome azienda e carica un bilancio per iniziare l'analisi.")
