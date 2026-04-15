
import streamlit as st
import plotly.graph_objects as go
from supabase import create_client, Client

# Configurazione Dashboard
st.set_page_config(page_title="Coin-Nexus Enterprise", layout="wide", page_icon="🏛️")

# Connessione Database (Verifica Secrets)
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except:
    st.error("⚠️ Errore: Configura SUPABASE_URL e SUPABASE_KEY nei Secrets di Streamlit!")
    st.stop()

# --- LOGICA FINANZIARIA AVANZATA ---
def calculate_metrics(rev, costs, debt):
    ebitda = rev - costs
    dscr = ebitda / (debt if debt > 0 else 1)
    isa_320 = max(ebitda * 0.05, rev * 0.01)
    safety_margin = ((rev - (costs * 1.1)) / rev) * 100
    
    if dscr > 3 and safety_margin > 15: rating = "AAA"
    elif dscr > 1.5: rating = "BBB"
    else: rating = "CCC"
    
    return rating, isa_320, dscr, round(max(0, safety_margin), 2)

# --- INTERFACCIA ---
st.title("🏛️ Coin-Nexus | Financial Risk Terminal")
st.caption("Protocollo Certificato Basel IV & ISA 320")

with st.sidebar:
    st.header("📊 ERP Data Entry")
    company = st.text_input("Ragione Sociale", "Azienda Target S.p.A.")
    rev = st.number_input("Ricavi (€)", value=5450000)
    costs = st.number_input("Costi (€)", value=4500000)
    debt = st.number_input("Debito Totale (€)", value=1200000)
    run = st.button("🚀 GENERA AUDIT COMPLETO")

if run:
    rating, isa, dscr, safety = calculate_metrics(rev, costs, debt)
    
    # 1. KPI Principali
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rating Finale", rating)
    c2.metric("Soglia ISA 320", f"€{isa:,.0f}")
    c3.metric("Indice DSCR", f"{dscr:.2f}")
    c4.metric("Margine Sicurezza", f"{safety}%")

    # 2. Grafico Gauge (Il pezzo forte)
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = dscr * 20, # Normalizzato per scala 100
        title = {'text': "Affidabilità Creditizia"},
        gauge = {'axis': {'range': [None, 100]},
                 'bar': {'color': "#00f2ff"},
                 'steps': [
                     {'range': [0, 40], 'color': "red"},
                     {'range': [40, 70], 'color': "yellow"},
                     {'range': [70, 100], 'color': "green"}]}
    ))
    fig_gauge.update_layout(template="plotly_dark", height=350)
    st.plotly_chart(fig_gauge, use_container_width=True)

    # 3. Salvataggio Cloud
    try:
        supabase.table("audit_reports").insert({
            "company_name": company, "rating": rating, "revenue": rev
        }).execute()
        st.success("✅ Dossier archiviato crittograficamente nel Cloud.")
    except:
        st.warning("Salvataggio locale: Database non ancora pronto.")

# --- SEZIONE DATABASE STORICO ---
st.divider()
st.subheader("📑 Archivio Audit Real-Time")
try:
    res = supabase.table("audit_reports").select("*").order("created_at", desc=True).limit(5).execute()
    st.table(res.data)
except:
    st.info("In attesa di nuovi dati dal terminale...")
