import streamlit as st

st.set_page_config(page_title="COIN-NEXUS TEST", page_icon="💠")

st.title("💠 COIN-NEXUS QUANTUM AI")
st.success("Il sistema è online!")

password = st.text_input("Inserisci Password di Licenza", type="password")

if password == "PLATINUM2026":
    st.write("### Accesso Autorizzato")
    st.info("Carica un file per iniziare l'analisi ISA e il Rating.")
    uploaded_file = st.file_uploader("Scegli un file Excel o CSV", type=['csv', 'xlsx'])
    
    if uploaded_file:
        st.write("File ricevuto con successo! Il motore Quantum è pronto.")
else:
    st.warning("In attesa di autenticazione...")
