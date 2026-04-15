import streamlit as st
import pandas as pd
from utils.parser import load_data, extract_financials
from engine.scoring import compute_score, risk_label

st.set_page_config(page_title="Coin-Nexus", layout="wide")

st.title("🏦 Coin-Nexus | Financial Intelligence")

uploaded = st.file_uploader("Upload ERP file", type=["csv", "xlsx"])

if uploaded:

    df = load_data(uploaded)
    st.subheader("Dati ERP")
    st.dataframe(df)

    financials = extract_financials(df)

    score, explanation = compute_score(financials)

    st.metric("Coin-Nexus Score", f"{score}/100")
    st.success(risk_label(score))

    st.subheader("Explainability")
    for e in explanation:
        st.write("•", e)
