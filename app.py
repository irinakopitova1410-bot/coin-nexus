import streamlit as st
import pandas as pd
# Import dai moduli (assicurati che esistano i file __init__.py nelle cartelle)
try:
    from engine.scoring import calculate_metrics
    from services.decision import get_credit_approval
except ImportError as e:
    st.error(f"Errore di importazione moduli: {e}. Controlla i file __init__.py")

# --- TITOLO E UI ---
st.title("🏛️ Coin-Nexus | Credit Decision Engine")

# Verifica se i Secrets sono configurati
if "SUPABASE_URL" not in st.secrets:
    st.warning("⚠️ Configura i Secrets (SUPABASE_URL e KEY) su Streamlit Cloud per attivare il database.")
else:
    st.success("✅ Connessione Cloud Pronta")

# --- LOGICA DI INPUT ---
with st.sidebar:
    st.header("Dati Aziendali")
    name = st.text_input("Ragione Sociale", "Esempio S.p.A.")
    rev = st.number_input("Ricavi (€)", value=1000000)
    ebitda = st.number_input("EBITDA (€)", value=200000)
    debt = st.number_input("Debito Totale (€)", value=400000)
if st.button("ESEGUI AUDIT BANCARIO"):

    metrics = calculate_metrics({
        "revenue": rev,
        "ebitda": ebitda,
        "debt": debt
    })

    decision = get_credit_approval(metrics)

    # ---------------- HEADER ----------------
    st.markdown("## 🏛️ Credit Decision Report")

    st.markdown(f"### 🏢 {name}")

    # ---------------- DECISION ----------------
    st.markdown(f"## 🏆 Rating: {decision['rating']}")
    st.markdown(f"### {decision['decision']}")

    if decision['decision'] == "APPROVATO":
        st.success("Alta probabilità di accesso al credito")
    elif decision['decision'] == "REVISIONE MANUALE":
        st.warning("Richiede valutazione manuale")
    else:
        st.error("Bassa probabilità di accesso al credito")

    # ---------------- VALORE ECONOMICO ----------------
    st.markdown("## 💰 Capacità di Credito Stimata")

    st.markdown(f"### € {decision.get('estimated_credit', 0):,.0f}")

    # ---------------- KPI VISUAL ----------------
    st.markdown("## 📊 Indicatori Finanziari")

    col1, col2, col3 = st.columns(3)

    col1.metric("DSCR", metrics.get("dscr", 0))
    col2.metric("Leverage", metrics.get("leverage", 0))
    col3.metric("Margin %", metrics.get("margin", 0))

    # ---------------- REPORT ----------------
    report = f"""
CREDIT AUDIT REPORT

Company: {name}

Rating: {decision['rating']}
Decision: {decision['decision']}

DSCR: {metrics.get('dscr')}
Leverage: {metrics.get('leverage')}

Estimated Credit: € {decision.get('estimated_credit', 0)}
"""

    st.download_button(
        "📥 Download Credit Report",
        report,
        file_name=f"Credit_Report_{name}.txt"
    )
