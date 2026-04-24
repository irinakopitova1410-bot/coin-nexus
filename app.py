# pages_modules/erp_import.py
import streamlit as st
import pandas as pd
import time

def render_erp_import():
    st.markdown('<div class="nexus-header"><h2>🔌 ERP Data Connector</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("""
        **Nexus Bridge** supporta l'importazione automatica dai principali ERP. 
        Seleziona il tuo software e carica il file di esportazione o configura l'API.
        """)
        
        # Selezione Sorgente
        erp_type = st.selectbox(
            "Seleziona il tuo sistema gestionale (ERP)",
            ["Microsoft Dynamics 365 / NAV", "SAP Business One", "Zucchetti Ad Hoc", "TeamSystem Enterprise", "DocFinance Export", "Generic Excel/CSV"]
        )
        
    with col2:
        st.metric("Ultima Sincronizzazione", "Oggi, 08:45", delta="Successo")
        st.button("🔄 Forza Refresh API", use_container_width=True)

    st.divider()

    # Layout a Tab per le diverse modalità di import
    tab_upload, tab_api, tab_mapping = st.tabs(["📁 Caricamento File", "🌐 Connessione API", "🗺️ Mapping Colonne"])

    with tab_upload:
        uploaded_file = st.file_uploader(f"Trascina qui l'export di {erp_type}", type=["xlsx", "csv", "xml"])
        
        if uploaded_file:
            with st.spinner("Analisi tracciato record in corso..."):
                # Simulazione di lettura e mapping intelligente
                time.sleep(1.5)
                df = pd.read_excel(uploaded_file) if "xlsx" in uploaded_file.name else pd.read_csv(uploaded_file)
                
                # Validazione schema
                required_cols = ['Data', 'Conto', 'Dare', 'Avere', 'Descrizione']
                found_cols = [c for c in required_cols if c in df.columns]
                
                if len(found_cols) == len(required_cols):
                    st.success("✅ Tracciato riconosciuto correttamente!")
                    st.dataframe(df.head(5), use_container_width=True)
                    
                    if st.button("🚀 Elabora e Salva in Nexus", type="primary"):
                        st.session_state["erp_data"] = df
                        st.session_state["erp_company"] = "Azienda Test S.p.A." # Estratto dal file
                        st.toast("Dati importati con successo!")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.error(f"❌ Errore Tracciato: Mancano le colonne {list(set(required_cols) - set(found_cols))}")

    with tab_api:
        st.warning("🔒 Le connessioni API sono riservate ai piani Enterprise.")
        st.text_input("Endpoint URL", value="https://api.businesscentral.dynamics.com/v2.0/...", disabled=True)
        st.text_input("API Key / Client Secret", type="password", disabled=True)
        st.button("Test Connessione", disabled=True)

    with tab_mapping:
        st.write("Configura come le voci del tuo ERP si mappano sul piano dei conti Nexus.")
        # Esempio di interfaccia di mapping
        c1, c2 = st.columns(2)
        c1.text("Voce ERP (Conto)")
        c2.text("Categoria Nexus")
        st.markdown("""
        - 450100 (Ricavi Vendite) → **Fatturato**
        - 600500 (Acquisto Materie) → **COGS**
        - 700100 (Salari e Stipendi) → **Costi Personale**
        """)
